from airflow import DAG
# from airflow.providers.mysql.transfers.mysql_to_s3 import MySQLToS3Operator
from airflow.operators.empty import EmptyOperator
# from airflow.providers.amazon.aws.transfers.s3_to_s3 import S3ToS3Operator

from datetime import datetime
from airflow.models import Variable

# Definisikan konfigurasi default_args untuk DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 8, 17),
    'depends_on_past': False,
    'retries': 1,
}

# Inisialisasi objek DAG
dag = DAG(
    'mysql_to_s3_etl',
    default_args=default_args,
    schedule_interval=None,  # Anda bisa menyesuaikan interval scheduling sesuai kebutuhan
    catchup=False,
)

# Mendapatkan konfigurasi dari Airflow Variables
aws_access_key_id = Variable.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = Variable.get("AWS_SECRET_ACCESS_KEY")
s3_bucket = Variable.get("S3_BUCKET")

# Definisikan tugas-tugas
extract_movie_task = EmptyOperator(task_id='extract_movie_task', dag=dag)

# extract_movie_task = MySQLToS3Operator(
#     task_id='extract_movie_task',
#     sql='SELECT * FROM movie',
#     mysql_conn_id='mysql_default',  # Sesuaikan dengan MySQL connection ID Anda
#     aws_conn_id='aws_default',      # Sesuaikan dengan AWS connection ID Anda
#     schema='movielens_movies_rating',
#     bucket_name=s3_bucket,
#     key='movie_data.csv',
#     aws_credentials_id='aws_default',
#     dag=dag,
# )

extract_rating_task = EmptyOperator(task_id='extract_rating_task', dag=dag)

# extract_rating_task = MySQLToS3Operator(
#     task_id='extract_rating_task',
#     sql='SELECT * FROM rating',
#     mysql_conn_id='mysql_default',  # Sesuaikan dengan MySQL connection ID Anda
#     aws_conn_id='aws_default',      # Sesuaikan dengan AWS connection ID Anda
#     schema='movielens_movies_rating',
#     bucket_name=s3_bucket,
#     key='rating_data.csv',
#     aws_credentials_id='aws_default',
#     dag=dag,
# )

# Definisi tugas transform_task untuk join tabel "movie" dan "rating"
transform_query = """
SELECT m.*, r.rating, r.timestamp
FROM movie m
JOIN rating r ON m.movieID = r.movieID
"""

transform_task = EmptyOperator(task_id='transform_task', dag=dag)

# transform_task = MySQLToS3Operator(
#     task_id='transform_task',
#     sql=transform_query,
#     mysql_conn_id='mysql_conn_id',  # Sesuaikan dengan MySQL connection ID Anda
#     aws_conn_id='aws_conn_id',      # Sesuaikan dengan AWS connection ID Anda
#     schema='movielens_movies_rating',
#     bucket_name=s3_bucket,
#     key='transformed_data.csv',
#     aws_credentials_id='aws_default',
#     dag=dag,
# )

# Definisi tugas load_task untuk memindahkan file hasil transformasi ke lokasi yang diinginkan di S3
load_task = EmptyOperator(task_id='load_task', dag=dag)

# load_task = S3ToS3Operator(
#     task_id='load_task',
#     source_bucket_key='s3://{}/transformed_data.csv'.format(s3_bucket),
#     dest_s3_conn_id='aws_default',
#     dest_bucket_name=s3_bucket,
#     dest_key='final_data.csv',
#     aws_conn_id='aws_default',
#     replace=True,
#     dag=dag,
# )

# Mengatur urutan tugas dengan dependencies
[extract_movie_task, extract_rating_task] >> transform_task >> load_task
