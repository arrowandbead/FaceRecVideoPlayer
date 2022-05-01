
from selenium import webdriver
import time
import requests
import shutil
import os


user = os.getlogin()
driver = webdriver.Chrome(executable_path='./chromedriver')

directory = 'C:\\Users'+'\\'+user+'\Desktop'
listCelebNames = ["Harry Styles"]
iterate = 15

def topLevelSearchExecute(listCelebNames, outputDirectory, driver):
    for celeb in listCelebNames:
        url = 'https://www.google.com/search?q='+str(celeb)+'&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947'
        hyphenName = '-'.join(celeb.split(' '))
        saveFolder = outputDirectory + "/" + hyphenName
        find_urls(hyphenName, saveFolder, url, driver, iterate)
def save_img(inp,img,i, saveFolder):
    try:
        filename = saveFolder + "/" + inp+str(i)+'.jpg'
        response = requests.get(img,stream=True)
        image_path = os.path.join(directory, filename)
        with open(image_path, 'wb') as file:
            shutil.copyfileobj(response.raw, file)
    except Exception:
        pass


def find_urls(inp, saveFolder, url,driver,iterate):
    os.mkdir(saveFolder)
    driver.get(url)
    time.sleep(3)
    for j in range (1,16):
        imgurl = driver.find_element_by_xpath('//div//div//div//div//div//div//div//div//div//div['+str(j)+']//a[1]//div[1]//img[1]')
        print(imgurl)
        input()
        imgurl.click()
        time.sleep(15)
        img = driver.find_element_by_xpath('//body/div[2]/c-wiz/div[3]/div[2]/div[3]/div/div/div[3]/div[2]/c-wiz/div[1]/div[1]/div/div[2]/a/img').get_attribute("src")
        save_img(inp,img,j, saveFolder)
        print("saved 1")
            

topLevelSearchExecute(listCelebNames, "./contestantPics", driver)