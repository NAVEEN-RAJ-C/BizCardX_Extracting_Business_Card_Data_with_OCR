import streamlit as st
import easyocr
from PIL import Image
from numpy import asarray
import re

reader = easyocr.Reader(['en'])


def extract_text(image):
    np_card = asarray(image)
    card_text = reader.readtext(np_card)
    return card_text


def segregate_info(info_list):
    states = ['Andhra Pradesh', 'Assam', 'Arunachal Pradesh', 'Bihar', 'Chhattisgarh', 'Gujarat', 'Goa',
              'Himachal Pradesh', 'Haryana', 'Jharkhand', 'Kerala', 'Karnataka', 'Maharashtra',
              'Madhya Pradesh', 'Manipur', 'Mizoram', 'Meghalaya', 'Nagaland', 'Odisha', 'Orissa', 'Punjab',
              'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'West Bengal', 'Uttarakhand',
              'Uttar Pradesh']
    uts = ['Delhi', 'Andaman and Nicobar Islands', 'Chandigarh', 'Puducherry',
           'Daman and Diu and Dadra and Nagar Haveli', 'Lakshadweep', 'Jammu and Kashmir', 'Ladakh']
    company_name = None
    card_holder_name = None
    designation = None
    mobile_number = None
    email_address = None
    website_url = None
    area = None
    city = None
    state = None
    ut = None
    pin_code = None

    for item in info_list:
        if re.search(r"\+", item):
            mobile_number = item
        elif re.search('@', item):
            email_address = item
        elif re.search('www', item.lower()[:3]):
            website_url = item
        elif item.isnumeric():
            pin_code = item
        elif item in states:
            state = item
        elif item in uts:
            ut = item
        elif item[-1].isnumeric():
            pin_code = item[-6:]
            state = item[:-7]
        else:
            if not company_name:
                company_name = item
            elif not card_holder_name:
                card_holder_name = item
            elif not designation:
                designation = item
            elif not area:
                area = item
            elif not city:
                city = item
    return {company_name, card_holder_name, designation, mobile_number, email_address, website_url, area, city,
            state, ut, pin_code}


def main():
    img = ''
    st.set_page_config(page_title='Extracting Business Card with OCR', layout='wide')
    st.title('BizCardX: Extracting Business Card Data with OCR')
    biz_card = st.file_uploader(label='Upload a Business Card', type='png')
    if biz_card is not None:
        img = Image.open(biz_card)
    if st.button('Extract text from the uploaded Business Card') and biz_card:
        texts = extract_text(img)
        details = []
        for text in texts:
            details.append(text[1])
        st.write(details)
        st.write(texts)
        company_name, card_holder_name, designation, mobile_number, email_address, website_url, area, \
            city, state, ut, pin_code = segregate_info(details)
        if ut is None:
            details_tag = dict(Company_Name=company_name, Card_Holder_Name=card_holder_name, Designation=designation,
                               Mobile_Number=mobile_number, E_mail=email_address, Site=website_url, Area=area,
                               City=city, State=state, PIN=pin_code)
        else:
            details_tag = dict(Company_Name=company_name, Card_Holder_Name=card_holder_name, Designation=designation,
                               Mobile_Number=mobile_number, E_mail=email_address, Site=website_url, Area=area,
                               City=city, UT=ut, PIN=pin_code)
        st.write(details_tag)


if __name__ == '__main__':
    main()
