from selenium import webdriver
import time
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import wget
import psycopg2


#Open page in web-browser
driver = webdriver.Firefox(executable_path="./geckodriver")
driver.get('https://www.italki.com/teachers/german')
time.sleep(10)

#Keep clicking Intro and More Teachers
for i in range(1,501):
    print(i)
    WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located((By.XPATH, '//div[@id="found-teacher-'+str(i)+'"]/descendant::span[contains(text(),"Intro")]')))
    teacher_card_head = driver.find_element_by_xpath('//div[@id="found-teacher-'+str(i)+'"]/descendant::span[contains(text(),"Intro")]').click()
    # intro=driver.find_element_by_xpath('//div[@id="found-teacher-'+str(i)+'"]/descendant::div[@class="teacher-card-tab-body"]/descendant::span').text
    elem = driver.find_element_by_xpath('//div[@id="found-teacher-'+str(i)+'"]/descendant::span[contains(text(),"Intro")]'
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", elem)

    if i%20 == 0:
        button = driver.find_element_by_class_name('teachers-more').click() 

soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()
teacher_divs = soup.findAll("div", {"class": "teacher-card"})

final_arr=[]
j = 1
for teacher in teacher_divs:
    if j<=500:
        teacher_card_information = teacher.find("div",{'teacher-card-information'})
        teacher_name_h1 = teacher_card_information.find('h1')
        teacher_name = teacher_name_h1.find('span').text
        
        teacher_card_intro = teacher.find("div",{'teacher-card-intro'})
        teacher_intro_p = teacher_card_intro.find("p")
        teacher_intro = teacher_intro_p.find("span").text

        teacher_price_h2 = teacher.find("h2",{'teacher-price-rate'})
        teacher_price = teacher_price_h2.find("span").text

        avatar_circle = teacher.find("span",{'ant-avatar-circle'})
        avatar_image = avatar_circle.find("img")
        avatar_src = avatar_image['src']

        #download image
        system_source = 'img/'+str(j)+'.jpg'
        wget.download(avatar_src, system_source)
        j=j+1
        
        final_arr.append({
            'name':teacher_name,
            'hourly_rate':teacher_price,
            'image_system_path': system_source,
            'intro':teacher_intro
        })

    else:
        break


#insert into database
def insertIntoDB(final_arr):
    try:
        connection = psycopg2.connect(user="postgres",
                                        password="postgres",
                                        host="127.0.0.1",
                                        port="5432",
                                        database="scraper")
        cursor = connection.cursor()

        for profiles in final_arr:
            postgres_insert_query = """ INSERT INTO scraper (name, hourly_rate,image_system_path,intro) VALUES (%s,%s,%s,%s)"""
            record_to_insert = (profiles['name'],profiles['hourly_rate'], profiles['image_system_path'],profiles['intro'])
            cursor.execute(postgres_insert_query, record_to_insert)

            connection.commit()
            count = cursor.rowcount
            print (count, "Record inserted successfully into mobile table")

    except (Exception, psycopg2.Error) as error :
        if(connection):
            print("Failed to insert record into mobile table", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

#calling database function with database object as parameter
insertIntoDB(final_arr)

