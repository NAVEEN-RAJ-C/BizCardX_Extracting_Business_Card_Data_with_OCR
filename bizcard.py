# importing the required libraries
import streamlit as st
import easyocr
from PIL import Image, ImageFilter
from numpy import asarray
import re
import mysql.connector
import io
import pandas as pd

# easyOCR reader language is set to english
reader = easyocr.Reader(['en'])

# Connect to the MySQL database
conn = mysql.connector.connect(host='localhost',
                               user='root',
                               password='pw',
                               database="bizcard")

# Create a cursor object to interact with the database
cursor = conn.cursor()


# function to split the image
def split_image(image):
    width, height = image.size

    # Calculate the midpoint to split the image
    mid = width // 2.18

    # Split the image into left and right halves
    left_half = image.crop((0, 0, mid, height))
    right_half = image.crop((mid, 0, width, height))

    return left_half, right_half


# function to extract text from image
def extract_text(image):
    # image is converted to numpy array
    np_card = asarray(image)
    # the array is read to extract text using easyOCR reader
    card_text = reader.readtext(np_card)
    return card_text


# function to segregate text from the list
def segregate_info(info_list):
    # Create an empty list to store the updated elements
    updated_info_list = []

    # Loop through the original list
    for item in info_list:
        # Split the item using commas
        separated_items = re.split(r'[,;]', item)

        # Remove any leading or trailing whitespace from the separated strings
        separated_items = [s.strip() for s in separated_items]

        # Extend the updated_info_list with the separated items
        updated_info_list.extend(separated_items)

    # Replace the original list with the updated list
    info_list = updated_info_list

    # initializing variables
    mobile_number = []
    email_address = ''
    website_url = []
    area = ''
    city = ''
    state = ''
    pin_code = ''

    for item in info_list[2:]:
        # finding mobile number using regular expression search
        if re.search(r"\d{3}-\d{4}", item):
            mobile_number.append(item)
        # finding email using regular expression search
        elif re.search('@', item):
            email_address = item
        # finding site using regular expression search
        elif re.search('www', item.lower()[:3]) or re.search('com', item.lower()[-3:]):
            website_url.append(item)
        # finding PIN and state using isnumeric
        elif item[-6:].isnumeric() and ' ' in item:
            id_space = item.index(' ')
            pin_code = item[id_space + 1:]
            state = item[:id_space]
        elif item.isnumeric():
            pin_code = item
        else:
            if not area:
                area = item
            elif not city:
                city = item
            elif not state:
                state = item
    # assigning cardholder name and designation by indexing
    card_holder_name = info_list[0]
    designation = info_list[1]
    return card_holder_name, designation, mobile_number, email_address, website_url, area, city, state, pin_code


# function to extract business_card_text
def extract_business_card_text(image):
    # splitting the image
    img_left, img_right = split_image(image)
    # extracting text from the left image
    texts_left = extract_text(img_left)
    # extracting text from the right image
    texts_right = extract_text(img_right)
    details_left = []
    details_right = []
    # appending extracted texts to separate lists
    for text in texts_left:
        details_left.append(text[1])

    for text in texts_right:
        details_right.append(text[1])
    # Finding out company name using if statement
    if len(details_left) > len(details_right):
        company_name = " ".join(details_right)
        card_holder_name, designation, mobile_number, email_address, website_url, area, \
            city, state, pin_code = segregate_info(details_left)
    else:
        company_name = " ".join(details_left)
        card_holder_name, designation, mobile_number, email_address, website_url, area, \
            city, state, pin_code = segregate_info(details_right)

    # Create a BytesIO object to hold binary data
    image_binary = io.BytesIO()

    # Save the image to the BytesIO object as binary data
    image.save(image_binary, format='PNG')  # Use the appropriate image format
    # Get the binary data as bytes
    binary_data = image_binary.getvalue()

    # details are structures in the form of dictionary
    details_tag = dict(Company_Name=company_name, Card_Holder_Name=card_holder_name, Designation=designation,
                       Mobile_Number=' '.join(mobile_number), E_mail=email_address, Website='.'.join(website_url),
                       Area=area, City=city, State_or_UT=state, PIN=int(pin_code), Business_Card=binary_data)

    return details_tag


# main function to run streamlit
def main():
    img = ''
    if 'details' not in st.session_state:
        st.session_state.details = []
    st.set_page_config(page_title='Extracting Business Card with OCR', layout='wide')
    st.markdown("<h1 style='text-align: center; font-size: 50px; '>BizCardX: Extracting Business Card Data with "
                "OCR</h1>", unsafe_allow_html=True)
    # Use st.markdown with HTML to create a horizontal line
    st.markdown("<hr style='border: 1px solid #ddd;'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h2 style='text-align: center; font-size: 25px;'>Uploading Image | Extracting Text | Storing in "
                    "SQL</h2>", unsafe_allow_html=True)
        st.write("")
        # Upload the Business Card image
        biz_card = st.file_uploader(label='UPLOAD A BUSINESS CARD', type='png')
        if biz_card is not None:
            # opening the image using pillow
            img = Image.open(biz_card)
            # sharpening the image
            img = img.filter(ImageFilter.SHARPEN)
        # Button to trigger the text extraction process
        if st.button('Extract text from the uploaded Business Card') and biz_card:
            with st.spinner("Extracting text..."):
                details_tag = extract_business_card_text(img)
                st.session_state.details.append(details_tag)
                details_df = pd.DataFrame(st.session_state.details)
                st.session_state.details_df = details_df
                st.session_state.details_df.drop_duplicates(inplace=True)
            st.spinner()  # Hide the spinner
            st.success('Extracted text from the Business Card image successfully')
            st.write('DETAILS OF THE BUSINESS CARD')
            # displaying the extracted text
            st.image(biz_card, caption="Uploaded Business Card", width=252, use_column_width=False)
            st.write(details_tag)
            st.dataframe(st.session_state.details_df)
        if 'details' in st.session_state:
            if st.button('Store the extracted information into SQL database'):

                details_df = st.session_state.details_df

                for row in details_df.itertuples(index=False):
                    details = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])

                    insert_query = 'INSERT INTO details VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                    try:
                        cursor.execute(insert_query, details)
                    except mysql.connector.IntegrityError:
                        continue
                conn.commit()
                st.success('Stored the extracted information into SQL database')

    # Add the vertical line between the columns
    c1.markdown("<div class='vertical-line'></div>", unsafe_allow_html=True)

    # column for modifying details stored in SQL table
    with c2:
        st.markdown("<h2 style='text-align: center; font-size: 25px;'>Modifying details in SQL</h2>",
                    unsafe_allow_html=True)
        st.write("")

        if st.button('Show SQL table'):
            # To show details stored in SQL table
            st.write('DETAILS STORED IN SQL DATABASE')
            query = 'select * from details'
            # reading SQL query using pandas
            query_df = pd.read_sql_query(query, conn)
            # Showing details stored in SQL table as dataframe
            st.dataframe(query_df)

        # fetching the cardholder names stored in SQL table
        cursor.execute('select card_holder_name from details')
        card_holder_rows = cursor.fetchall()
        if card_holder_rows:
            # list of cardholders
            card_holders = [row[0] for row in card_holder_rows]
            # selection of a cardholder name to modify her or his details
            card_holder = st.selectbox('SELECT A CARD HOLDER WHOSE DETAILS ARE TO BE UPDATED', ['None'] + card_holders,
                                       index=0)
            st.session_state.card_holder = card_holder
            # list of details
            details_list = ['Company_Name', 'Card_Holder_Name', 'Designation', 'Mobile_Number', 'E_mail', 'Website',
                            'Area', 'City', 'State_or_UT', 'PIN']
            # Multiselect widget to select the details to be changed
            change_details = st.multiselect('SELECT THE DETAILS TO BE CHANGED', details_list, default=[])
            st.session_state.change_details = change_details

        if st.session_state.change_details:
            # Dictionary to store the new values entered by the user
            if 'new_values_dict' not in st.session_state:
                st.session_state.new_values_dict = {}

            # Create text boxes dynamically based on selected details and store the new values in the dictionary
            if st.session_state.change_details:
                for detail in st.session_state.change_details:
                    new_value = st.text_input(f'Enter new value to be updated for {detail}')
                    st.session_state.new_values_dict[detail] = new_value
            # Update the table with the new values
            if st.button('Update the values') and st.session_state.new_values_dict:
                for detail, new_value in st.session_state.new_values_dict.items():
                    # SQL UPDATE query
                    update_query = f"UPDATE details SET {detail} = %s WHERE Card_Holder_Name = %s"

                    # Execute the UPDATE query with the new value
                    cursor.execute(update_query, (new_value, st.session_state.card_holder))

                # Commit the changes to the database
                conn.commit()
                st.success('Details updated successfully')

        st.markdown("<h2 style='text-align: center; font-size: 25px;'>Removing card holder details from SQL table</h2>",
                    unsafe_allow_html=True)
        st.write("")
        if card_holder_rows:
            # list of cardholders
            card_holders_to_remove = [row[0] for row in card_holder_rows]
            # selection of a cardholder name to modify her or his details
            card_holder_name_to_remove = st.selectbox('SELECT A CARD HOLDER WHOSE DETAILS ARE TO BE REMOVED',
                                                      ['None'] + card_holders_to_remove, index=0)
        if st.button('Remove') and card_holder_name_to_remove:
            # Execute the DELETE query
            delete_query = f"DELETE FROM details WHERE Card_Holder_Name = '{card_holder_name_to_remove}'"
            cursor.execute(delete_query)

            # Commit the changes
            conn.commit()
            st.success(f'{card_holder_name_to_remove}\'s details removed successfully')

        st.markdown("<h2 style='text-align: center; font-size: 25px;'>To clear the entire SQL table</h2>",
                    unsafe_allow_html=True)
        st.write("")
        if st.button('Click here to clear the table'):
            cursor.execute('delete from details')
            conn.commit()
            st.write('SQL table cleared')


if __name__ == '__main__':
    main()
