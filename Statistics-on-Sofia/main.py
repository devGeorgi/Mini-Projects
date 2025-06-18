import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import concurrent.futures
import random

# List of cities to compare with Sofia
cities = [
    "Тирана", "Киев", "Кишинев", "Анкара", "Истанбул", "Белград", "Атина", 
    "Лисабон", "Сараево", "Скопие", "Подгорица", "Прищина", "Минск", "Рига",
    "Будапещ", "Никозия", "Букурещ", "Братислава", "Вилнос", "Рим", "Талин",
    "Делхи", "Любляна", "Москва", "Валета", "Прага", "Шанхай", "Пекин",
    "Загреб", "Варшава", "Нью-Йорк", "Париж", "Мадрид", "Виена", "Лондон",
    "Токио", "Рейкявик", "Андора ла Веля", "Дъблин", "Осло", "Берлин",
    "Брюксел", "Детройт", "Вашингтон", "Амстердам", "Стокхолм", "Хелскинки",
    "Копенхаген", "Вашингтон", "Берн", "Люксембург", "Вадуц", "Сан Марино",
    "Монако"
]

# City and country mappings (Cyrillic name: [Latin city name, Country])
city_country_mappings = {
    "Тирана": ["Tirana", "Albania"],
    "Киев": ["Kiev (Kyiv)", "Ukraine"],
    "Кишинев": ["Chisinau", "Moldova"],
    "Анкара": ["Ankara", "Turkey"],
    "Истанбул": ["Istanbul", "Turkey"],
    "Белград": ["Belgrade", "Serbia"],
    "Атина": ["Athens", "Greece"],
    "Лисабон": ["Lisbon", "Portugal"],
    "Сараево": ["Sarajevo", "Bosnia And Herzegovina"],
    "Скопие": ["Skopje", "North Macedonia"],
    "Подгорица": ["Podgorica", "Montenegro"],
    "Прищина": ["Pristina", "Kosovo (Disputed Territory)"],
    "Минск": ["Minsk", "Belarus"],
    "Рига": ["Riga", "Latvia"],
    "Будапещ": ["Budapest", "Hungary"],
    "Никозия": ["Nicosia", "Cyprus"],
    "Букурещ": ["Bucharest", "Romania"],
    "Братислава": ["Bratislava", "Slovakia"],
    "Вилнос": ["Vilnius", "Lithuania"],
    "Рим": ["Rome", "Italy"],
    "Талин": ["Tallinn", "Estonia"],
    "Делхи": ["Delhi", "India"],
    "Любляна": ["Ljubljana", "Slovenia"],
    "Москва": ["Moscow", "Russia"],
    "Валета": ["Valletta", "Malta"],
    "Прага": ["Prague", "Czech Republic"],
    "Шанхай": ["Shanghai", "China"],
    "Пекин": ["Beijing", "China"],
    "Загреб": ["Zagreb", "Croatia"],
    "Варшава": ["Warsaw", "Poland"],
    "Нью-Йорк": ["New York, NY", "United States"],
    "Париж": ["Paris", "France"],
    "Мадрид": ["Madrid", "Spain"],
    "Виена": ["Vienna", "Austria"],
    "Лондон": ["London", "United Kingdom"],
    "Токио": ["Tokyo", "Japan"],
    "Рейкявик": ["Reykjavik", "Iceland"],
    "Андора ла Веля": ["Andorra la Vella", "Andorra"],
    "Дъблин": ["Dublin", "Ireland"],
    "Осло": ["Oslo", "Norway"],
    "Берлин": ["Berlin", "Germany"],
    "Брюксел": ["Brussels", "Belgium"],
    "Детройт": ["Detroit, MI", "United States"],
    "Вашингтон": ["Washington, DC", "United States"],
    "Амстердам": ["Amsterdam", "Netherlands"],
    "Стокхолм": ["Stockholm", "Sweden"],
    "Хелскинки": ["Helsinki", "Finland"],
    "Копенхаген": ["Copenhagen", "Denmark"],
    "Берн": ["Bern", "Switzerland"],
    "Люксембург": ["Luxembourg", "Luxembourg"],
    "Вадуц": ["Vaduz", "Liechtenstein"],
    "Сан Марино": ["San Marino", "San Marino"],
    "Монако": ["Monaco", "Monaco"]
}

def get_city_comparison(city, max_retries=3):
    """Scrape comparison data for a given city vs Sofia"""
    if city not in city_country_mappings:
        return {'city': city, 'status': 'error', 'error': 'City not found in mappings'}
        
    city_info = city_country_mappings[city]
    search_city = city_info[0]
    search_country = city_info[1]
    
    for attempt in range(max_retries):
        try:
            base_url = "https://www.numbeo.com/cost-of-living/compare_cities.jsp"
            
            # Properly encode the parameters
            params = {
                "country1": "Bulgaria",
                "city1": "Sofia",
                "country2": search_country,
                "city2": search_city
            }
            
            # Create the request URL with properly encoded parameters
            query_string = urllib.parse.urlencode(params)
            request_url = f"{base_url}?{query_string}"
            
            # Debug info
            debug_info = f"Request URL: {request_url}"
            
            # Reduced sleep time with random jitter to be less detectable
            time.sleep(0.2 + random.random() * 0.3)  # Random delay between 0.2-0.5 seconds
            response = requests.get(request_url, timeout=10)
            
            # Check for HTTP errors
            if response.status_code != 200:
                return {
                    'city': city, 
                    'status': 'error', 
                    'error': f'HTTP error {response.status_code}',
                    'debug': debug_info
                }
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for various error conditions in the page content
            if "Please select a city" in response.text:
                return {
                    'city': city, 
                    'status': 'error', 
                    'error': 'City not found on Numbeo',
                    'debug': debug_info
                }
            
            if "An error occurred" in response.text:
                return {
                    'city': city, 
                    'status': 'error', 
                    'error': 'Numbeo returned an error',
                    'debug': debug_info
                }
            
            purchasing_power = None
            salary_difference = None
            no_purchasing_power_data = False
            
            # Try to find the relevant data
            for row in soup.find_all('tr'):
                text = row.get_text()
                if "Local Purchasing Power" in text:
                    if "Not enough data to calculate difference in Local Purchasing Power" in text:
                        no_purchasing_power_data = True
                        # Continue checking for salary data
                        continue
                    try:
                        # Check if purchasing power is higher or lower
                        if "lower" in text:
                            # If lower, make the percentage negative
                            purchasing_power = -float(text.split('%')[0].split()[-1])
                        else:
                            purchasing_power = float(text.split('%')[0].split()[-1])
                    except (ValueError, IndexError):
                        pass
                elif "Average Monthly Net Salary" in text:
                    try:
                        salary_text = row.find_all('td')[-1].get_text()
                        if '%' in salary_text:
                            # Check if salary is higher or lower
                            if "lower" in salary_text:
                                # If lower, make the percentage negative
                                salary_difference = -float(salary_text.strip().split('%')[0])
                            else:
                                salary_difference = float(salary_text.strip().split('%')[0])
                    except (ValueError, IndexError):
                        pass
            
            # Changed condition to allow missing purchasing power if explicitly noted
            if (purchasing_power is None and not no_purchasing_power_data) or salary_difference is None:
                return {
                    'city': city, 
                    'status': 'error', 
                    'error': 'Could not parse purchasing power or salary data',
                    'debug': debug_info
                }
                
            return {
                'city': city,
                'purchasing_power': purchasing_power,
                'salary_difference': salary_difference,
                'no_purchasing_power_data': no_purchasing_power_data,
                'status': 'success'
            }
            
        except requests.exceptions.ConnectionError:
            if attempt == max_retries - 1:
                return {'city': city, 'status': 'error', 'error': 'Network connection failed'}
            continue
            
        except requests.exceptions.Timeout:
            if attempt == max_retries - 1:
                return {'city': city, 'status': 'error', 'error': 'Request timed out'}
            continue
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                return {'city': city, 'status': 'error', 'error': f'Request error: {str(e)}'}
            continue
            
        except Exception as e:
            return {'city': city, 'status': 'error', 'error': f'Unexpected error: {str(e)}'}
    
    return {'city': city, 'status': 'error', 'error': 'Max retries exceeded'}

def main():
    results = []
    successful_cities = 0
    total_cities = len(cities)
    
    print("== RESULTS ==")
    
    # Use ThreadPoolExecutor to run requests in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Create a future for each city
        future_to_city = {}
        for city in cities:
            future = executor.submit(get_city_comparison, city)
            future_to_city[future] = city
        
        # Process results in the order of cities list
        for city in cities:
            # Find the future for this city
            for future, c in future_to_city.items():
                if c == city:
                    try:
                        result = future.result()
                        
                        if result['status'] == 'success':
                            successful_cities += 1
                            if 'no_purchasing_power_data' in result and result['no_purchasing_power_data']:
                                print(f"{result['city']}: No purchasing power data | {result['salary_difference']}%")
                            else:
                                print(f"{result['city']}: {result['purchasing_power']}% | {result['salary_difference']}%")
                        else:
                            error_message = f"Couldn't get data for {result['city']}: {result['error']}"
                            print(error_message)
                    except Exception as e:
                        print(f"Error processing {city}: {str(e)}")
                    break
    
    # Summary
    print(f"\nSummary: Successfully retrieved data for {successful_cities} out of {total_cities} cities")

if __name__ == "__main__":
    main()
