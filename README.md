# Resume-Parser-AWS-Event-Driven-Workflow

Prerequisite For Lambda Layer Creation:

![Untitled Jam 1](https://github.com/ashutosh6500/Resume-Parser-AWS-Event-Driven-Workflow/assets/65476854/db14d428-bfd5-4341-97a9-83193b8be06c)


Commands on Ubuntu EC2 Instance:
```
sudo apt-get update
sudo apt install zip
mkdir -p build/python/lib/python3.10/site-packages
pip3 install PyMuPDF regex -t build/python/lib/python3.10/site-packages
zip -r pymupdf.zip build/
sudo apt install awscli
aws s3 cp pymupdf.zip s3://<path>
```


Steps:

![image](https://github.com/ashutosh6500/Resume-Parser-AWS-Event-Driven-Workflow/assets/65476854/6fbb37a8-a638-4623-a0e2-7b1fc2a43a49)

Basic Idea :
```
When user uploads resume pdf file to S3 bucket,it triggers lambda function which parse the resume using fitz module and extracts basic information like contact number,Email id etc and puts it in DynamoDB table.After deleting file,it deletes that record from DynamoDB Table.Also it sends mail to subscribed users using SNS service.
```
