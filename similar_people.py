from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from pyvirtualdisplay import Display
from collections import deque
from selenium.common.exceptions import NoSuchElementException
import sys

driver = webdriver.Firefox()

def main():
    #uncomment to run display virtually on xvfb
    #display = Display(visible=0)
    #display.start()
    
    driver.get("http://www.google.com")
    assert "Google" in driver.title
    
    if len(sys.argv) < 2:
        print "Please enter a search term"
        driver.close()
        #display.stop()
        return

    initial_name = str(sys.argv[1])

    j = 2
    while j < len(sys.argv):
        initial_name += str(" " + sys.argv[j])
        j += 1

    #dictionary to ensure no repeated names
    mydict = {initial_name : None}
    search_bar = driver.find_element_by_xpath("//input[@id='lst-ib']")
    search_bar.send_keys(initial_name)
    search_bar.send_keys(Keys.RETURN)
    driver.implicitly_wait(5)

    try:
        driver.find_element_by_xpath("//a[contains(text(), 'People also search for')]").click()
    except NoSuchElementException:
        print "This person is lonely"
        return
    driver.implicitly_wait(5)

    #list of similar people as web elements, 1 degree removed
    similar_list_temp = driver.find_elements_by_xpath("//div[@class='kltat']")

    similar_list = list();
    #add list to file
    #overwrites if file already exists
    with open('list.txt', 'w') as myfile:
        myfile.write("Degree 1 connections: \n")
        for s in similar_list_temp:
            similar_list.append(s.text)
            #1st degree, no collisions
            mydict.update({s.text : None})
            myfile.write(s.text + "\t")
        myfile.write("\n")

    i = 1
    search(similar_list, mydict, i)

    myfile.close()
    driver.close()    
    #display.stop()

#recursively searches for all contacts within 3 degrees
def search(similar_list, mydict, i):
    new_list = list()
    for person in similar_list:
        #search and get new similar_list, append to queue
        find_similar(person, new_list, mydict) 
        #if j == 3: #only find 2nd degree for first 3, shorter run
         #   break
        #j += 1

    #append new_list to file
    with open('list.txt', 'a+') as myfile:
        myfile.write("\n"+ "degree "+ str(i+1) + " connections: \n")
        for name in new_list:
            myfile.write(name.encode('utf8') + "\t")
        myfile.write("\n")
    #recurse until i == 2 to find 3rd degree connections
    if i < 2:
        search(new_list, mydict, i+1)


#find similar people and add to new_list
def find_similar(person, new_list, mydict):
    #searches for person
    driver.get("http://www.google.com")
    search_bar = driver.find_element_by_xpath("//input[@id='lst-ib']")
    search_bar.send_keys(person)
    search_bar.send_keys(Keys.RETURN)
    driver.implicitly_wait(5)
    try:
        driver.find_element_by_xpath("//a[contains(text(), 'People also search for')]").click()
    except NoSuchElementException:
        return
    driver.implicitly_wait(5)

    #append similar people's names to list
    #only add if not already in dictionary/hashtable
    for s in driver.find_elements_by_xpath("//div[@class='kltat']"):
        if(not mydict.has_key( s.text )):
            mydict.update({ s.text  : None })
            new_list.append(s.text)

if __name__ == "__main__": main()
