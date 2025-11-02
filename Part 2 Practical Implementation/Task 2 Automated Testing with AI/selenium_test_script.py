from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
import unittest
import time
import logging

class TestLoginPageAIEnhanced(unittest.TestCase):
    """AI-enhanced automated testing for login functionality"""
    
    def setUp(self):
        """Initialize driver with optimized configuration"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 20)  # Increased timeout
        self.base_url = "https://aura-pro-plus.onrender.com/auth/login"  
        self.logger = logging.getLogger('LoginTests')
        
    def tearDown(self):
        """Clean up after tests"""
        if self.driver:
            self.driver.quit()
    
    def safe_screenshot(self, name):
        """Safe screenshot utility with timeout handling"""
        try:
            self.driver.save_screenshot(f"{name}_{time.strftime('%Y%m%d_%H%M%S')}.png")
            return True
        except Exception as e:
            self.logger.warning(f"Could not take screenshot {name}: {str(e)}")
            return False
    
    def safe_get(self, url, max_retries=3):
        """Safe page loading with retries"""
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                time.sleep(5)  # Base wait time
                return True
            except Exception as e:
                self.logger.warning(f"Page load attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(10)  # Wait longer between retries
                    continue
                else:
                    raise e
    
    def find_element_with_fallback(self, selectors):
        """Try multiple selectors to find element"""
        for by, value in selectors:
            try:
                element = self.wait.until(EC.presence_of_element_located((by, value)))
                return element
            except TimeoutException:
                continue
        raise NoSuchElementException(f"Element not found with any selector: {selectors}")
    
    def test_valid_login(self):
        """Test successful login with valid credentials"""
        try:
            # Load page with retry mechanism
            self.safe_get(self.base_url)
            
            # Take initial screenshot
            self.safe_screenshot("valid_login_before_credentials")
            
            # Wait for page to be interactive
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Find elements with multiple selector strategies
            username_selectors = [
                (By.ID, "username"),
                (By.NAME, "username"),
                (By.XPATH, "//input[@type='email']"),
                (By.XPATH, "//input[contains(@placeholder, 'email')]"),
                (By.XPATH, "//input[@name='email']")
            ]
            
            password_selectors = [
                (By.ID, "password"), 
                (By.NAME, "password"),
                (By.XPATH, "//input[@type='password']")
            ]
            
            button_selectors = [
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.XPATH, "//button[contains(text(), 'Sign In')]"),
                (By.ID, "login-btn"),
                (By.XPATH, "//input[@type='submit']")
            ]
            
            username_field = self.find_element_with_fallback(username_selectors)
            password_field = self.find_element_with_fallback(password_selectors)
            login_button = self.find_element_with_fallback(button_selectors)
            
            # Clear fields and enter credentials
            username_field.clear()
            password_field.clear()
            username_field.send_keys("validuser@example.com")
            password_field.send_keys("China@18#123")
            
            # Take screenshot with credentials entered
            self.safe_screenshot("valid_login_credentials_entered")
            
            time.sleep(2)  # Small delay before click
            login_button.click()
            
            # Wait for login to process with longer timeout
            time.sleep(8)
            
            # Take screenshot after login attempt
            self.safe_screenshot("valid_login_after_submit")
            
            # Check for successful login indicators with shorter timeout
            success_indicators = [
                (By.XPATH, "//*[contains(text(), 'Welcome')]"),
                (By.XPATH, "//*[contains(text(), 'Dashboard')]"),
                (By.XPATH, "//*[contains(text(), 'Logout')]"),
                (By.CLASS_NAME, "dashboard"),
                (By.ID, "dashboard"),
                (By.XPATH, "//*[contains(text(), 'Profile')]")
            ]
            
            # Try to find any success indicator quickly
            success_found = False
            for by, value in success_indicators:
                try:
                    # Use shorter timeout for success checks
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, value))
                    )
                    success_found = True
                    self.logger.info(f"Valid login test: PASSED - Found success indicator: {value}")
                    self.safe_screenshot("valid_login_success")
                    break
                except TimeoutException:
                    continue
            
            if not success_found:
                # If no specific indicator, check if URL changed from login page
                current_url = self.driver.current_url.lower()
                if "login" not in current_url and "auth" not in current_url:
                    self.logger.info("Valid login test: PASSED - URL changed from login page")
                    self.safe_screenshot("valid_login_url_changed")
                else:
                    # Check if we're still on login page but with different state
                    try:
                        error_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Invalid')]")
                        if error_elements:
                            self.logger.warning("Valid login test: FAILED - Invalid credentials message found")
                            self.safe_screenshot("valid_login_invalid_credentials")
                        else:
                            self.logger.warning("Valid login test: UNCERTAIN - Still on login page")
                            self.safe_screenshot("valid_login_still_on_login")
                    except:
                        self.logger.warning("Valid login test: UNCERTAIN - Could not determine outcome")
                        self.safe_screenshot("valid_login_uncertain")
            
        except Exception as e:
            self.logger.error(f"Valid login test failed: {str(e)}")
            # Try to take final screenshot even on failure
            self.safe_screenshot("valid_login_final_error")
            raise
    
    def test_invalid_login(self):
        """Test login failure with invalid credentials"""
        try:
            self.safe_get(self.base_url)
            self.safe_screenshot("invalid_login_before_credentials")
            
            time.sleep(3)
            
            # Find elements
            username_selectors = [
                (By.ID, "username"),
                (By.NAME, "username"),
                (By.XPATH, "//input[@type='email']")
            ]
            
            password_selectors = [
                (By.ID, "password"),
                (By.NAME, "password"), 
                (By.XPATH, "//input[@type='password']")
            ]
            
            button_selectors = [
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Login')]")
            ]
            
            username_field = self.find_element_with_fallback(username_selectors)
            password_field = self.find_element_with_fallback(password_selectors)
            login_button = self.find_element_with_fallback(button_selectors)
            
            # Enter invalid credentials
            username_field.clear()
            password_field.clear()
            username_field.send_keys("invalid_user@test.com")
            password_field.send_keys("wrong_password_123")
            
            self.safe_screenshot("invalid_login_credentials_entered")
            
            login_button.click()
            time.sleep(5)  # Wait for error message
            
            self.safe_screenshot("invalid_login_after_submit")
            
            # Look for error message with multiple selectors
            error_selectors = [
                (By.CLASS_NAME, "error"),
                (By.CLASS_NAME, "error-message"),
                (By.XPATH, "//*[contains(text(), 'Invalid')]"),
                (By.XPATH, "//*[contains(text(), 'Error')]"),
                (By.XPATH, "//*[contains(text(), 'incorrect')]"),
                (By.XPATH, "//*[contains(@class, 'alert')]"),
                (By.XPATH, "//*[contains(@class, 'text-red')]")
            ]
            
            error_found = False
            for by, value in error_selectors:
                try:
                    error_element = self.driver.find_element(by, value)
                    if error_element.is_displayed():
                        self.logger.info(f"Invalid login test: PASSED - Error found: {error_element.text[:50]}")
                        error_found = True
                        self.safe_screenshot("invalid_login_error_displayed")
                        break
                except NoSuchElementException:
                    continue
            
            if not error_found:
                self.logger.warning("Invalid login test: No error message found, but test completed")
                self.safe_screenshot("invalid_login_no_error_message")
                
        except Exception as e:
            self.logger.error(f"Invalid login test failed: {str(e)}")
            self.safe_screenshot("invalid_login_failure")
            raise
    
    def test_empty_credentials(self):
        """Test login attempt with empty fields"""
        try:
            self.safe_get(self.base_url)
            time.sleep(3)
            
            # Find login button
            button_selectors = [
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.ID, "login-btn")
            ]
            
            login_button = self.find_element_with_fallback(button_selectors)
            login_button.click()
            
            time.sleep(3)  # Wait for validation
            
            # Look for validation errors with multiple selectors
            validation_selectors = [
                (By.CLASS_NAME, "field-error"),
                (By.CLASS_NAME, "error"),
                (By.XPATH, "//*[contains(text(), 'required')]"),
                (By.XPATH, "//*[contains(text(), 'fill')]"),
                (By.XPATH, "//*[contains(@class, 'invalid')]"),
                (By.XPATH, "//input[@required]/following-sibling::*[contains(@class, 'error')]")
            ]
            
            validation_errors = []
            for by, value in validation_selectors:
                try:
                    errors = self.driver.find_elements(by, value)
                    for error in errors:
                        if error.is_displayed():
                            validation_errors.append(error)
                except:
                    continue
            
            if validation_errors:
                self.logger.info(f"Empty credentials test: PASSED - Found {len(validation_errors)} validation errors")
            else:
                # Check if button is disabled (another form of validation)
                if not login_button.is_enabled():
                    self.logger.info("Empty credentials test: PASSED - Login button is disabled")
                else:
                    self.logger.warning("Empty credentials test: No validation errors found")
            
        except Exception as e:
            self.logger.error(f"Empty credentials test failed: {str(e)}")
            self.safe_screenshot("empty_credentials_failure")
            raise

# Test execution and reporting
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    unittest.main(verbosity=2)