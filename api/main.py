from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import qrcode
import boto3
import os
from io import BytesIO
import logging
from botocore.exceptions import ClientError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Loading Environment variable (AWS Access Key and Secret Key)
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Allowing CORS for local!
origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Validate AWS credentials
aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRET_KEY")

if not aws_access_key or not aws_secret_key:
    logger.error("AWS credentials not found in environment variables")
    raise ValueError("AWS credentials not properly configured")

# AWS S3 Configuration
try:
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )
except Exception as e:
    logger.error(f"Failed to initialize S3 client: {str(e)}")
    raise

bucket_name = os.getenv("BUCKET_NAME") # S3 bucket name

@app.post("/generate-qr/")
async def generate_qr(url: str):
    try:
        # Log the incoming request
        logger.info(f"Generating QR code for URL: {url}")

        # Generate QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR Code to BytesIO object
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Generate file name for S3
        file_name = f"qr_codes/{url.split('//')[-1].replace('/', '_')}.png"
        
        # Verify bucket exists
        try:
            s3.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"Bucket {bucket_name} does not exist")
                raise HTTPException(status_code=500, detail=f"S3 bucket {bucket_name} does not exist")
            elif error_code == '403':
                logger.error(f"Access denied to bucket {bucket_name}")
                raise HTTPException(status_code=500, detail="Access denied to S3 bucket")
        
        # Upload to S3 without ACL
        try:
            s3.put_object(
                Bucket=bucket_name,
                Key=file_name,
                Body=img_byte_arr,
                ContentType='image/png'
            )
            
            # Generate the S3 URL
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
            logger.info(f"Successfully uploaded QR code to: {s3_url}")
            return {"qr_code_url": s3_url}
            
        except ClientError as e:
            error_message = str(e)
            logger.error(f"Failed to upload to S3: {error_message}")
            raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {error_message}")
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
