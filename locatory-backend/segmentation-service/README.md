General set up:

Python 3.8+ is required to run this file.
Run the requirements.txt file using the following command:
pip install -r requirements.txt
Note: Mention the correct path of requirements.txt in the above command

Segmentation-service

    About

        There are three API calls:
            1. /token
            2. /rfm/rfm_segmentation_with_saved_data
            3. /rfm/rfm_segmentation_with_parameters

        The detailed API documentation will be available on localhot:8000/docs url after running the API.
        The file test_rfm_apis.ipynb under tests/rfmtests/ has sample calls of the above three APIs.
        The APIs 2 and 3 are secured with OAuth2 authentication. API 1 returns a Bearer token that is required to access APIs 2 and 3.

    Functionality

        This microservice performs RFM (Recency, Frequency, Monetary) segmentation using the customer data and their order history data stored in Mongo-DB.
        The service uses Mini-Batch K-Means clustering method to cluster customer's Frequency and Monetary values.

    Setup and Start

        The directory structure is as follows:
        -> segmentation-service (repository)
            -> app (package)
                -> api (package)
                    -> rfm (package that contains rfm endpoints and code files)
                -> clustering_models (directory containing saved clustering models)
                -> logs (directory containing log files)
                -> tests (package)
                    -> rfmtests (package that contains rfm tests and test_rfm_apis.ipynb files) 

        All of the above directories must exists before starting the service.

        Create a .env file inside app/ package using the .env.example template. Ask am754815@dal.ca for API credentials.

        Command to start the service:
        Inside segmentation-service/ run: uvicorn app.main:app

        General Approach to API calls:
        Firstly, call the /token API using valid username and password. The /token API returns a token that can be used for RFM related API calls. The file test_rfm_apis.ipynb under tests/rfmtests/ has sample calls of the above three APIs.

    Common Http Codes and meaning (response message could be different)
    
        1. 200 - success
        2. 401 - Authentication error
        3. 400 - Document not found / No order data found
        4. 422 - Unprocessable entity
        5. 500 - Unexpected error

If there are any issues or questions, please contact am754815@dal.ca.