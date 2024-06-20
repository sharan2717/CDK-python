import json
from multiprocessing import process
import urllib.parse
import boto3

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
   
def calculateMarks(marks_csv):

    rows = marks_csv.splitlines()[1:]

    # Filter out empty first elements (assuming headers are on the first line)
    filtered_rows = [row for row in rows if row.strip()]

    processed_data = []
    for row in filtered_rows:
        columns = row.split(",")
        name = columns[0].strip()
        marks = dict(zip(["Tamil", "English", "Maths", "Science", "Social"], 
                     map(lambda x: float(x.strip()), columns[1:])))
        gpa = calculate_gpa(marks)

        processed_data.append({
            "Name":name ,
            "Tamil": calculate_grade(marks["Tamil"]),
            "English": calculate_grade(marks["English"]),
            "Maths": calculate_grade(marks["Maths"]),
            "Science": calculate_grade(marks["Science"]),
            "Social": calculate_grade(marks["Social"]),
            "GPA": round(gpa, 2),
        })

    return processed_data

def calculate_gpa(marks):
   
   credit_points = {
      "Tamil": 1,
      "English": 2,
      "Maths": 3,
      "Science": 2,
      "Social": 2,
  }
   grade_values = {"A+": 10, "A": 9, "B+": 8, "B": 7, "C": 6, "D": 5}
 
   total_credit_points = 0
   total_grade_points = 0

   for subject, mark in marks.items():
     grade = calculate_grade(mark) 
     credit_point = credit_points.get(subject) 

     if credit_point is None:
       print(f"Warning: Subject '{subject}' not found in credit points dictionary.")
       continue  

     grade_value = grade_values.get(grade)  

     if grade_value is None:
       print(f"Warning: Grade '{grade}' not found in grade values dictionary.")
       continue  

     total_credit_points += credit_point
     total_grade_points += grade_value * credit_point

   if total_credit_points == 0:
     return 0.0 

   return total_grade_points / total_credit_points

def addStudentGrades(grades):
   try:
     table = dynamodb.Table(process.env.TABLE_NAME)
     with table.batch_writer() as batch:
        for item in grades:
              batch.put_item(Item=item)  
   except Exception as e:
        raise e
 
def calculate_grade(mark):
    if (mark >= 90):
        return "A+"
    elif (mark >= 80):
       return "A";
    elif (mark >= 70): 
        return "B+";
    elif  (mark >= 60):
        return "B";
    elif  (mark >= 40): 
        return "C";
    else:
        return "D";


def getCSVContent(response):
   try:
     with response['Body'] as fileobj:
        csv_string = fileobj.read().decode('utf-8')
        return csv_string
   except Exception as e:
        print(e)
        print('Error getting object from bucket ')
        raise e
   

def main(event, context):
    print("event is ", event )
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        marks_csv = getCSVContent(response)
        grades=calculateMarks(marks_csv)
        addStudentGrades(grades)
        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
    
    