# Loop Assignment 

### Technology used 
* Flask
* pandas


---
* To start the application just run following command:
    `pip install`
    and execute the `run.py` file to start the server

 ---
###  Note: you must have python 3.9 or above installed on your system 

 * Demo data from the Assignment document is already present in the database.

    ### Base URL: http://localhost:5000 or http://localhost:8080

    ### API Endpoints:

    * [POST] /trigger_report -> this api is used to start generating report

        ```
        Request Body ->
        {
            "limit":300
        }
      
      
      /// limit attribute in Request body is used to 
      /// the restaurents you want to include in the report 
      /// since the processing time is in hours for ~13000
      /// restaurents, you can use this property for validating 
      /// the result for small section
      
      /// However is you dont pass it into the body 
      /// it will generate report for all the restaurents
      /// present in the database [this will take approx 2 hours]
      
      /// since this is a post request you have to pass an empty body
      /// if you are not sending a limit key
      

        Response ->
        {
           "report_id": "TLULATZ"
        }       
        ```

    * [POST] /get_report -> this api is used get status or get the file if it is generated

        ```
        Request Body ->
        {
            "report_id":"TLULATZ"
        }
      
      
        /// possible responses
        Response ->
        {
            "status": "generating"
        }  
        Response ->
        {
            "status": "File not present"
        }      
        Response -> TLULATZ.csv
        ```


-----
Thank You

Shubham Gautam 

www.shubhamgautam.live
