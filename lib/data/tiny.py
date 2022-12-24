from typing import Optional
from operator import attrgetter
from datetime import datetime
import os
from aiotinydb import AIOTinyDB
import boto3

DB_BACKUP_DIR = "tinydb/"
DB_LOCAL_FILE_NAME = "db.json"
DB_FILE_DIR = "./{}".format(DB_LOCAL_FILE_NAME)

BUCKET_NAME_ENV_VAR = "DISCORD_BOT_S3_BUCKET"


def get_db(backup_name: Optional[str] = None):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket("andy-bot-dev")
    if backup_name:
        db_backup_obj = bucket.Object(key="{}{}".format(DB_BACKUP_DIR, backup_name))
        db_backup_obj.download_file(DB_FILE_DIR)
    else:
        s3_response = bucket.objects.filter(Prefix=DB_BACKUP_DIR)
        sorted_db_backup_objs = sorted(s3_response, key=attrgetter("last_modified"))
        last_modified_backup_obj = sorted_db_backup_objs.pop()
        last_modified_backup_obj.Object().download_file(DB_FILE_DIR)


def backup_db():
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(os.getenv(BUCKET_NAME_ENV_VAR, "andy-bot-dev"))
    with open(DB_LOCAL_FILE_NAME, "rb") as db_file:
        bucket.put_object(
            Key="{}andy-bot-backup-{}".format(DB_BACKUP_DIR, datetime.now()),
            Body=db_file,
        )


