Streamlit Business Card Data Extraction Application

Introduction

This Streamlit application allows users to upload an image of a business card and extract relevant information from it using easyOCR. The extracted information includes the company name, card holder name, designation, mobile number, email address, website URL, area, city, state, and pin code.

The extracted information is then displayed in a clean and organized manner in the application's graphical user interface (GUI). Users can easily add the extracted information along with the uploaded business card image to a MySQL database. The database stores multiple entries, each containing its own business card image and extracted information.

Features

Upload an image of a business card and extract relevant information using easyOCR.
Display the extracted information in a clean and organized manner in the GUI.
Save the extracted information along with the uploaded image to a MySQL database.
View, update, and delete data from the database through the Streamlit interface.
Simple and intuitive user interface for a smooth user experience.

Requirements

Python, Streamlit, easyOCR  mysql-connector-python

Usage

Run the application:

streamlit run app.py

Upload the business card image:

Click the "Upload Business Card" button and select an image file containing a business card.
Extracted Information:

The application will use easyOCR to extract the relevant information from the uploaded image.
The extracted details will be displayed on the interface.

Save to Database:

If the extracted information is correct, click the "Store the extracted information into SQL database" button.
The information, along with the uploaded image, will be stored in the MySQL database.

View, Update, and Delete Data:

Use the "Show SQL table" button to view details stored in the MySQL database.
Select a card holder from the list to modify their details and click the "Update the values" button to save the changes.
Use the "SELECT CARD HOLDER(s) WHOSE DETAILS ARE TO BE REMOVED" dropdown to select card holders whose details you want to remove. Click the "Remove" button to delete the selected card holder's details from the database.
To clear the entire MySQL table, click the "Click here to clear the table" button.

Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.

License

This project is licensed under the MIT License