import boto3
import logging

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Initialize boto3 client
    ec2 = boto3.client('ec2')
    
    # Log the entire event for debugging purposes
    logger.info(f"Received event: {event}")
    
    try:
        # Extract Volume ID from the event resources
        resources = event.get('resources', [])
        if not resources:
            raise ValueError("Resources list is empty.")
        
        volume_arn = resources[0]  # Assuming the first resource is the volume
        volume_id = volume_arn.split('/')[-1]
        
        if not volume_id:
            raise ValueError("Volume ID not found in event.")
        
        logger.info(f"Fetching details for volume {volume_id}")
        
        # Describe the volume to get its details
        volume = ec2.describe_volumes(VolumeIds=[volume_id])['Volumes'][0]
        
        # Check if the volume is of type gp2
        if volume['VolumeType'] == 'gp2':
            logger.info(f"Volume {volume_id} is of type gp2. Proceeding with conversion.")
            
            # Modify the volume to convert it to gp3
            ec2.modify_volume(
                VolumeId=volume_id,
                VolumeType='gp3'
            )
            
            logger.info(f"Volume {volume_id} successfully converted to gp3.")
            return {
                'statusCode': 200,
                'body': f"Volume {volume_id} successfully converted from gp2 to gp3."
            }
        else:
            logger.warning(f"Volume {volume_id} is not of type gp2. Current type: {volume['VolumeType']}.")
            return {
                'statusCode': 400,
                'body': f"Volume {volume_id} is not of type gp2. Current type: {volume['VolumeType']}."
            }
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': str(e)
        }
