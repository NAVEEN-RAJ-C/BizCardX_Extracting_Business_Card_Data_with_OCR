# importing the required libraries
import streamlit as st
import easyocr
from PIL import Image, ImageFilter
from numpy import asarray
import re

# easyOCR reader language is set to english
reader = easyocr.Reader(['en'])


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
    # details are structures in the form of dictionary
    details_tag = dict(Company_Name=company_name, Card_Holder_Name=card_holder_name, Designation=designation,
                       Mobile_Number=' '.join(mobile_number), E_mail=email_address, Site='.'.join(website_url),
                       Area=area, City=city, State_or_UT=state, PIN=pin_code)

    return details_tag


# main function to run streamlit
def main():
    img = ''
    st.set_page_config(page_title='Extracting Business Card with OCR', layout='wide')
    st.title('BizCardX: Extracting Business Card Data with OCR')
    # Upload the Business Card image
    biz_card = st.file_uploader(label='Upload a Business Card', type='png')
    if biz_card is not None:
        # opening the image using pillow
        img = Image.open(biz_card)
        # sharpening the image
        img = img.filter(ImageFilter.SHARPEN)
    # Button to trigger the text extraction process
    if st.button('Extract text from the uploaded Business Card') and biz_card:
        with st.spinner("Extracting text..."):
            details_tag = extract_business_card_text(img)
        st.spinner()  # Hide the spinner
        st.success('Extracted text from the Business Card image successfully')
        st.write('Details of the Business Card')
        # displaying the extracted text
        st.write(details_tag)


if __name__ == '__main__':
    main()
