#|export
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import psutil
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from fuzzywuzzy import fuzz
from logging_config import get_logger

logger = get_logger("script_file")
logger.debug("This is a debug message from the script file")
logger.info("This is an info message from the script file")

class FormEntry():
    def __init__(self,element):
        self.element = element
        self.label = None
        self.answer = None
        self.tag = None
        self.ID = None
        self.answer_type = None

    def __str__(self):
        return f'ID: {self.ID}, tag: {self.tag}, entry label: {self.label}, answer: {self.answer}, answer type: {self.answer_type}'
    
    def check_popup_list_visible(self):
        if len(self.element.find_elements_by_xpath(f"//descendant::div[@data-automation-id='activeListContainer']")) > 0:
            return True
        else:
            return False

    def get_answer_type(self):
        if self.tag == 'div':
            if self.element.get_attribute('data-automation-id') == 'dateInputWrapper':
                self.answer_type = 'DATE'
                day_input = self.element.find_elements_by_xpath(f"//*[@id='{self.ID}']/descendant::input[@aria-label='Day']")
                month_input = self.element.find_elements_by_xpath(f"//*[@id='{self.ID}']/descendant::input[@aria-label='Month']")
                year_input = self.element.find_elements_by_xpath(f"//*[@id='{self.ID}']/descendant::input[@aria-label='Year']")
                if len(day_input) > 0 and len(month_input) > 0 and len(year_input) > 0:
                    self.answer_type = 'DATE_MONTH_DAY_YEAR'
                elif len(month_input) > 0 and len(year_input) > 0:
                    self.answer_type = 'DATE_MONTH_YEAR'
                elif len(month_input) > 0:
                    self.answer_type = 'DATE_MONTH'
                elif len(year_input) > 0:
                    self.answer_type = 'DATE_YEAR'

            elif self.element.get_attribute('data-automation-id') == 'disability':
                self.answer_type = 'DISABILITY'
                
        elif self.tag == 'input':
            if self.element.get_attribute('type') == 'checkbox':
                self.answer_type = 'CHECKBOX'
            elif self.element.get_attribute('data-uxi-widget-type') == 'selectinput':
                self.answer_type = "MULTISELECT"
            elif self.element.get_attribute('type') == 'text':
                self.answer_type = "TEXTINPUT"

        elif self.tag == 'button':
            if self.element.get_attribute('type') == 'button':
                self.answer_type = "LISTBOX"

        elif self.tag == 'textarea':
            self.answer_type = 'TEXTAREA'
        

    def get_id(self):
        self.ID = self.element.get_attribute('ID')
        
    def get_label(self):        
        #get label based on if input or button element
        if self.answer_type == "DATE_MONTH_DAY_YEAR":
            label = self.element.find_element_by_xpath(f".//preceding-sibling::label")
            label = label.text
            label = label.replace("*", "")
            self.label = label

        elif self.answer_type == "DATE_MONTH_YEAR":
            label = self.element.find_element_by_xpath(f".//preceding-sibling::label")
            label = label.text
            label = label.replace("*", "")
            self.label = label

        elif self.answer_type == "DATE_YEAR":
            label = self.element.find_element_by_xpath(f".//preceding-sibling::label")
            label = label.text
            label = label.replace("*", "")
            self.label = label
            
        elif self.answer_type == "TEXTAREA":  
            label = self.element.find_element_by_xpath(f".//preceding::label[@for='{self.ID}']")
            label = label.text
            label = label.replace("*", "")
            self.label = label

        elif self.answer_type == "MULTISELECT":
                label = self.element.find_element_by_xpath(f".//preceding::label[@for='{self.ID}']")
                label = label.text
                label = label.replace("*", "")
                self.label = label
        
        elif self.answer_type == "LISTBOX":
            label = self.element.find_element_by_xpath(f".//preceding::label[@for='{self.ID}']")
            label = label.text
            label = label.replace("*", "")
            self.label = label

        elif self.answer_type == "DISABILITY":
            label = self.element.find_element_by_xpath(f"//legend[@for='{self.ID}']")
            label = label.text
            label = label.replace("*", "")
            self.label = label

        elif self.element.tag_name == 'input':
            try:
                label = self.element.find_element_by_xpath(f".//preceding::label[@for='{self.ID}']")
                label = label.text
                label = label.replace("*", "")
                self.label = label
            except:
                print(f"error, input has no ID")
                
        elif self.element.tag_name == 'div':
            try:
                label = self.element.find_element_by_xpath(".//preceding::legend[starts-with(@for, 'input-')]")
                label = label.text
                label = label.replace("*", "")
                self.label = label
            except:
                print("couldn't get div label")

        elif self.element.tag_name == 'button':
            #label = element.get_attribute('data-automation-id')
            #self.label = label.text
            label = self.element.find_element_by_xpath(f".//preceding::label[@for='{self.element.get_attribute('ID')}']")
            label = label.text
            label = label.replace("*", "")
            self.label = label
        else:
            print(f"Failed to get a label, ID: {self.element.get_attribute('ID')}")

    def add_answer(self,answer):
        self.answer = answer
    
    def get_tag(self):
        self.tag = self.element.tag_name

    def write_answer(self,driver):
        #Wait for element to be present
        EC.presence_of_element_located((By.ID, self.ID))
        
        #get desired answer
        desired_answer = self.answer.split(',')
        desired_answer = desired_answer[0]
        logger.info(f"deisred answer is: {desired_answer}")   
        
        #fill i nanswer based on type of form entry elemnt using self.answer_type: this will ultimately replace the self.tag method
        if self.answer_type == "DATE_MONTH_DAY_YEAR":
            date_input = self.element.find_element_by_xpath(f"//*[@id='{self.ID}']/descendant::input[@aria-label='Month']")
            #format answr for inputting correct date (this assumes date has formate mm/dd/yyyy)
            desired_answer = desired_answer.split('-')
            logger.info(f"desired answer split into: {len(desired_answer)} pieces")
            day = desired_answer[2].split(' ')
            desired_answer = desired_answer[1] + day[0] + desired_answer[0]
            logger.info(f"desired answer updated for date, is: {desired_answer}")
            
            date_input.send_keys(desired_answer)
            date_input.send_keys(Keys.TAB)

        elif self.answer_type == "DATE_MONTH_YEAR":
    
            date_input = self.element.find_element_by_xpath(f"//*[@id='{self.ID}']/descendant::input[@aria-label='Month']")
            #format answr for inputting correct date (this assumes date has formate mm/dd/yyyy)
            desired_answer = desired_answer.split('/')
            desired_answer = desired_answer[0] + desired_answer[2]
            
            date_input.send_keys(desired_answer)
            date_input.send_keys(Keys.TAB)

        elif self.answer_type == "DATE_YEAR":
            date_input = self.element.find_element_by_xpath(f"//*[@id='{self.ID}']/descendant::input[@aria-label='Year']")
            #format answer for inputting correct date (this assumes date has formate mm/dd/yyyy)
            desired_answer = desired_answer.split('/')
            desired_answer = desired_answer[2]
            print(desired_answer)
            date_input.send_keys(desired_answer)
            date_input.send_keys(Keys.TAB)  
            
        elif self.answer_type == "CHECKBOX":
            if desired_answer in ["yes", "YES", "Yes"] and self.element.get_attribute('aria-checked') == 'false':
                print("made it to here")
                self.element.click()
                time.sleep(0.5)

        elif self.answer_type == "TEXTAREA":
            #clear out any previous answer
            self.element.send_keys(Keys.CONTROL,"a", Keys.DELETE)

            #fill in desired answer
            self.element.send_keys(self.answer)
            self.element.send_keys(Keys.ENTER)
        
        elif self.answer_type == "MULTISELECT":
            #clear out any previous answer
            self.element.send_keys(Keys.CONTROL,"a", Keys.DELETE)
    
            #fill in desired answer
            self.element.send_keys(desired_answer)
            self.element.send_keys(Keys.ENTER)

            #Wait for a moment
            driver.implicitly_wait(1)
            
            if self.check_popup_list_visible() is True:
                listbox_choice = driver.find_element_by_xpath(f"//div[@data-automation-id='promptOption' and @data-automation-label='{desired_answer}']")
                listbox_choice.click()

            self.element.send_keys(Keys.TAB)

        elif self.answer_type == "LISTBOX":
            self.element.click()
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-uxi-widget-type='popup']")))
            dropdown_answer = self.element.find_element_by_xpath(f"//div[@data-uxi-widget-type='popup']/descendant::div[normalize-space(text())='{desired_answer}']")
            dropdown_answer.click()

        elif self.answer_type == "DISABILITY":
            answer_label = self.element.find_element_by_xpath(rf'//label[normalize-space(text())="{self.answer}"]')
            answer_label_id = answer_label.get_attribute('for')
            answer_checkbox = self.element.find_element_by_xpath(f"//input[@id='{answer_label_id}']")
            if answer_checkbox.get_attribute('aria-checked') == 'false':
                answer_checkbox.click()

        #fill in answer based on type of entry form
        elif self.tag == 'input':
            
            #clear out any previous answer
            self.element.send_keys(Keys.CONTROL,"a", Keys.DELETE)

            #fill in desired answer
            self.element.send_keys(desired_answer)
            self.element.send_keys(Keys.ENTER)

            #Wait for a moment
            driver.implicitly_wait(0.5)

            #if options box pops up select first option
            widget_tag = self.element.get_attribute('data-uxi-widget-type')
            
            #check if only certain options allowed and choose first one
            if widget_tag == 'selectinput':
                popup_element = self.element.find_element_by_xpath(f"//div[@data-uxi-widget-type = 'popup']")
                if popup_element.get_attribute('data-automation-activepopup') == "True":
                    listbox_choice = driver.find_element_by_xpath(f"//div[@data-automation-id='promptOption' and @data-automation-label='{desired_answer}']")
                    listbox_choice.click()

            self.element.send_keys(Keys.TAB)
            driver.implicitly_wait(0.4)

        elif self.tag == 'div':
            radios = self.element.find_elements_by_xpath(".//input[@type='radio']")
            #currently only treating radio buttons as yes or no, otehr types will raise error
            if len(radios) > 0:
                radio_label_yes = self.element.find_element_by_xpath(".//input[@type='radio']/following::label[normalize-space(text())='Yes']")
                radio_label_no = self.element.find_element_by_xpath(".//input[@type='radio']/following::label[normalize-space(text())='No']")
                radio_yes_idx = radio_label_yes.get_attribute('for')
                radio_no_idx = radio_label_no.get_attribute('for')
                radio_btn_yes = radio_label_yes.find_element_by_xpath(f".//preceding::input[@id='{radio_yes_idx}' and @type='radio']")
                radio_btn_no = radio_label_no.find_element_by_xpath(f".//preceding::input[@id='{radio_no_idx}' and @type='radio']")
                
                #check appropriate box
                if self.answer == 'Yes':
                    radio_btn_yes.click()
                else:
                    radio_btn_no.click()

            else:
                print(f"unkown what format the answer type is for ID: {self.element.get_attribute('ID')}")
        
        elif self.tag == 'button':
            self.element.click()
            driver.implicitly_wait(0.6)
            
            if len(self.element.find_elements_by_xpath(f"//div[@data-uxi-widget-type='popup']")) > 0:
                dropdown_answer = self.element.find_element_by_xpath(f"//div[@data-uxi-widget-type='popup']/descendant::div[normalize-space(text())='{desired_answer}']")
                dropdown_answer.click()
            elif len(self.element.find_elements_by_xpath(f"//div[@data-uxi-widget-type='popup']")) > 0:
                dropdown_answer = self.element.find_element_by_xpath(f"//div[@data-uxi-widget-type='popup']/descendant::div[normalize-space(text())='{desired_answer}']")
                print("On phone device type button")
                dropdown_answer.click()
            


    def update_element(self,driver):
        self.element = driver.find_element_by_xpath(f"//*[@id='{self.ID}']")


        #try alternative answer if desired fails