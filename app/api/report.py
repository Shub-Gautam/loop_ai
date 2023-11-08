import asyncio
import datetime
from flask_restful import Resource, reqparse
from app.utils import csv_util
from flask import send_from_directory, request
from sqlalchemy import MetaData
import sqlite3 as sql
import pandas as pd
import threading
import os
import pathlib
import app as ap

import app.utils.csv_util
curr_dir = os.path.dirname(pathlib.Path().resolve())
eSource = os.path.join(curr_dir, "loop", "instance", "StoreDatabase.db")

def another_thread(_loop,rand_str):
    coro = csv_util.generate_report(rand_str)
    future = asyncio.run_coroutine_threadsafe(coro, _loop)
    print(f"{threading.current_thread().name}: {future.result()}")


class ReportGenerator(Resource):

    def get(self):
        print("Report Generation =====================")
        opt_param = request.json.get("limit")
        if opt_param is None:
            limit = 3000000
        else:
            limit = request.get_json()["limit"]

        rand_str = csv_util.gen_report_id()
        print(rand_str)
        with sql.connect(eSource) as con:
            cur = con.cursor()
            cur.execute("INSERT INTO ReportStatus (reportId,status) VALUES (?,?)", (str(rand_str), "generating"))
            con.commit()

        x = threading.Thread(target=csv_util.generate_report, args=(rand_str,limit,))
        x.start()

        return {"report_id":str(rand_str)}

class Report(Resource):
    def __init__(self):
        self.req = reqparse.RequestParser()
        self.req.add_argument('report_id', type=str)

    def get(self):
        try:
            report_id = request.get_json()["report_id"]
            with sql.connect(eSource) as con:
                con.row_factory = sql.Row
                cur = con.cursor()
                cur.execute("SELECT status FROM ReportStatus WHERE reportId = '{}'".format(report_id))
                status = cur.fetchone();
                con.commit()
                if (status['status'] == "completed"):

                    return send_from_directory(directory=os.path.join(curr_dir,"loop","generated_csv") ,path=f'{report_id}.csv' , as_attachment=True)

                else:
                    return {"status":str(status['status'])}
        except:
            return {"status":"File not present"}