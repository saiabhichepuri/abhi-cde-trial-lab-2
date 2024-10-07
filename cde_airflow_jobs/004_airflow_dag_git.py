#****************************************************************************
# (C) Cloudera, Inc. 2020-2022
#  All rights reserved.
#
#  Applicable Open Source License: GNU Affero General Public License v3.0
#
#  NOTE: Cloudera open source products are modular software products
#  made up of hundreds of individual components, each of which was
#  individually copyrighted.  Each Cloudera open source product is a
#  collective work under U.S. Copyright Law. Your license to use the
#  collective work is as provided in your written agreement with
#  Cloudera.  Used apart from the collective work, this file is
#  licensed for your use pursuant to the open source license
#  identified above.
#
#  This code is provided to you pursuant a written agreement with
#  (i) Cloudera, Inc. or (ii) a third-party authorized to distribute
#  this code. If you do not have a written agreement with Cloudera nor
#  with an authorized and properly licensed third party, you do not
#  have any rights to access nor to use this code.
#
#  Absent a written agreement with Cloudera, Inc. (“Cloudera”) to the
#  contrary, A) CLOUDERA PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY
#  KIND; (B) CLOUDERA DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED
#  WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT LIMITED TO
#  IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND
#  FITNESS FOR A PARTICULAR PURPOSE; (C) CLOUDERA IS NOT LIABLE TO YOU,
#  AND WILL NOT DEFEND, INDEMNIFY, NOR HOLD YOU HARMLESS FOR ANY CLAIMS
#  ARISING FROM OR RELATED TO THE CODE; AND (D)WITH RESPECT TO YOUR EXERCISE
#  OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, CLOUDERA IS NOT LIABLE FOR ANY
#  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR
#  CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO, DAMAGES
#  RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF
#  BUSINESS ADVANTAGE OR UNAVAILABILITY, OR LOSS OR CORRUPTION OF
#  DATA.
#
# #  Author(s): Paul de Fusco
#***************************************************************************/

# Airflow DAG
from datetime import datetime
from airflow import DAG
from cloudera.cdp.airflow.operators.cde_operator import CDEJobRunOperator
from airflow.operators.dummy_operator import DummyOperator
import logging

username = "csso_schepuri"
dag_name = "BankFraudHol-" + username
logger = logging.getLogger(__name__)

print("Using DAG Name: {}".format(dag_name))

default_args = {
    'owner': username,
    'depends_on_past': False,
    'start_date': datetime(2024, 5, 21)
}

dag = DAG(
    dag_name,
    default_args=default_args,
    catchup=False,
    schedule_interval='@once',
    is_paused_upon_creation=False
)

start = DummyOperator(
    task_id="start",
    dag=dag
)

bronze = CDEJobRunOperator(
    task_id='data-ingestion',
    dag=dag,
    job_name='001_Lakehouse_Bronze_' + username,  # Must match name of CDE Spark Job in the CDE Jobs UI
    trigger_rule='all_success',
)

silver = CDEJobRunOperator(
    task_id='iceberg-merge-branch',
    dag=dag,
    job_name='002_Lakehouse_Silver_' + username,  # Must match name of CDE Spark Job in the CDE Jobs UI
    trigger_rule='all_success',
)

gold = CDEJobRunOperator(
    task_id='gold-layer',
    dag=dag,
    job_name='003_Lakehouse_Gold_' + username,  # Must match name of CDE Spark Job in the CDE Jobs UI
    trigger_rule='all_success',
)

end = DummyOperator(
    task_id="end",
    dag=dag
)

start >> bronze >> silver >> gold >> end
