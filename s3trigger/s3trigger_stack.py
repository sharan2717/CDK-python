
from aws_cdk import (
    aws_lambda as _lambda,
    aws_s3 as _s3,
    aws_s3_notifications,
    Stack
)
from constructs import Construct

class S3TriggerStack(Stack):
     

     def __init__(self,scope : Construct , id :str)->None :
          
           super().__init__(scope,id)

           function = _lambda.Function(self, "Lambda" , 
                                       code= _lambda.Code.from_asset("/lambda/"),
                                       handler="lambdahandler.main",
                                       runtime = _lambda.Runtime.PYTHON_3_9,
                                       function_name = "calculate_grade"
                                       )
           

           s3 = _s3.Bucket(self,"s3bucket")
           notification = aws_s3_notifications.LambdaDestination(function)

           s3.add_event_notification(_s3.EventType.OBJECT_CREATED,notification)