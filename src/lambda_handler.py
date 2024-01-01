import json
import re
import boto3
import time
import fitz

aws_access_key_id = '<ACCESS_KEY_ID>'
aws_secret_access_key = '<SECRET_KEY_ID>'
topic_arn = "<TOPIC_ARN>"
subject = "Resume Parser Operation"
country_code = re.compile(r"\+\d{1,3}")
contact_no = re.compile(r"\d{10}")
mail_id = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')

def sns(message,subject):
	client = boto3.client("sns",aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
	client.publish(TopicArn = topic_arn,Message = message,Subject =subject)
def lambda_handler(event, context):
	print(event)
    # boto3 client
	s3 = boto3.client('s3',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
	
	if(event):
		file_obj = event["Records"][0]
		# fetching bucket name from event
		bucketName = str(file_obj["s3"]["bucket"]["name"])
		# fetching file name from event
		fileName = str(file_obj["s3"]["object"]["key"])
		deleteOperation = False
		if(file_obj["eventName"].split(':')[0] == "ObjectRemoved"):
			deleteOperation = True
		if(not deleteOperation):
			# retrieving object from S3
			fileObj = s3.get_object(Bucket=bucketName, Key=fileName)
			# reading botocore stream
			file_content = fileObj["Body"].read()
			text = " "
			name = " "
			contactNo = " "
			mailId = " "
			countryCode = " "
			#using pyMuPdf fitz module to read pdf
			try:
				with fitz.open(stream=file_content,filetype="pdf") as doc:
					#iterating through pdf pages
					for page in doc:
						content = str(page.get_text())
						content = list(content.split())
						for line in content:
							line = str(line)
							#print(line)
							if(contactNo == " "):
								match = re.search(contact_no,line)
								if(match):
									contactNo = str(match.group())
							if(countryCode == " "):
								match = re.search(country_code,line)
								if(match):
									countryCode = str(match.group())
							if(mailId == " "):
								match = re.search(mail_id,line)
								if(match):
									mailId = str(match.group())
							if(name == " " and line):
								name = str(line)
	
			except Exception as e:
				raise e
			#creating json to send to dynamodb table
			
			data = {
				"name" : name,
				"contactNo" : (countryCode+"-"+contactNo),
				"mailId" : mailId,
				"fileName" : fileName
			}
			#print(data)
			#Initializing boto3 for dynamodb
			dynamodb_client = boto3.resource('dynamodb',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
			table = dynamodb_client.Table("Candidates")
		
			#add operation
			try:
				response = table.put_item(Item = data)
				message = "Successfully Added " + fileName + "Record To Table"
				sns(message,subject)
				return table.scan()
			except Exception as e:
				message = "Error occured during add operation due to Exception: " + str(e)
				sns(message,subject)
				raise e
		else:
			#delete opration
			dynamodb_client = boto3.resource('dynamodb',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
			table = dynamodb_client.Table("Candidates")
			try:
				response = table.delete_item(Key = {"fileName" : fileName})
				message = "Successfully Deleted " + fileName + "Record From Table"
				sns(message,subject)
				return table.scan()
			except Exception as e:
				message = "Failed to Delete " + fileName + "record due to Exception : "+str(e)
				sns(message,subject)
				raise e
			
	return {"statusCode" : 200,"body":json.dumps("done")}