import csv
import urllib
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import socket
import http.client
import traceback
import io
import re
from langdetect import detect
from translate import Translator
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import os
from Test_Web import classify
from translate import Translator
import six

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../Data-Services-43df957aab7d_NL_API.json'
file = r'../url_test.csv'

output_file = r'../output.txt'

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
f = io.open(output_file, 'a', encoding='utf8')
scrapped_data = ''
with open(file) as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for url in readCSV:

        print(url[0])

        req = urllib.request.Request('http://' + url[0], headers={'User-Agent': user_agent})

        try:
            urlopen(req, timeout=10)

        except HTTPError as e:
            http_e = url[0] + '|HTTP_Error||' + str(e.code) + '||'
            print(http_e)
            # scrapped_data.append(http_e)
            scrapped_data = http_e

            f.write(scrapped_data + '\n')

        except urllib.error.URLError as e:
            # url_e = url[0]+';URL_Error;'+e.response
            url_e = url[0] + '|URL_Error||' + str(e.reason) + '||'
            print(url_e)
            # scrapped_data.append(url_e)
            scrapped_data = url_e

            f.write(scrapped_data + '\n')

        except socket.error:
            socket_e = url[0] + '|Socket_Error||||'
            print(socket_e)
            # scrapped_data.append(socket_e)
            scrapped_data = socket_e

            f.write(scrapped_data + '\n')

        except http.client.HTTPException:
            http_e = url[0] + '|HTTP_Exception||||'
            print(http_e)
            # scrapped_data.append(http_e)
            scrapped_data = http_e

            f.write(scrapped_data + '\n')

        except (http.client.IncompleteRead) as e:
            http_e = url[0] + '|HTTP_CLIENT_IncompleteRead||||'
            print(http_e)
            # scrapped_data.append(http_e)
            scrapped_data = http_e

            f.write(scrapped_data + '\n')


        except Exception:
            # checksLogger.error('generic exception: ' + traceback.format_exc())
            e = url[0] + '|Exception||' + traceback.format_exc() + '||'
            print(e)
            # scrapped_data.append(e)
            scrapped_data = e

            f.write(scrapped_data + '\n')


        else:

            try:
                html = urlopen(req).read()


            except http.client.IncompleteRead as e:
                http_e = url[0] + '|HTTP_CLIENT_IncompleteRead||||'
                print(http_e)
                # scrapped_data.append(http_e)
                scrapped_data = http_e

                f.write(scrapped_data + '\n')

            except urllib.error.URLError as e:
                # url_e = url[0]+';URL_Error;'+e.response
                url_e = url[0] + '|URL_Error||' + str(e.reason) + '||'
                print(url_e)
                # scrapped_data.append(url_e)
                scrapped_data = url_e

                f.write(scrapped_data + '\n')

            except HTTPError as e:
                http_e = url[0] + '|HTTP_Error||' + str(e.code) + '||'
                print(http_e)
                # scrapped_data.append(http_e)
                scrapped_data = http_e

                f.write(scrapped_data + '\n')

            except socket.error:
                socket_e = url[0] + '|Socket_Error||||'
                print(socket_e)
                # scrapped_data.append(socket_e)
                scrapped_data = socket_e

                f.write(scrapped_data + '\n')

            except Exception:
                # checksLogger.error('generic exception: ' + traceback.format_exc())
                e = url[0] + '|Exception|' + traceback.format_exc() + '|||'
                print(e)
                # scrapped_data.append(e)
                scrapped_data = e

                f.write(scrapped_data + '\n')

            soup = BeautifulSoup(html, "html.parser")
            meta = soup.find_all('meta')
            try:
                for tag in meta:
                    if 'name' in tag.attrs.keys() and tag.attrs['name'].strip().lower() in ['description',
                                                                                            'og:description']:

                        web_desc = tag.attrs['content'].replace('|', ' ')

                        description = re.sub(r"\s+", " ", web_desc)
                        print("Description ...", description)
                        try:
                           lang = detect(description)

                        except:
                            print('LangDetect: LANGUAGE DETECT ERROR')

                        if len(description) > 10 and 'en' in lang:
                            document = types.Document(content=description.encode('utf-8'),
                                                      type=enums.Document.Type.PLAIN_TEXT)

                            client = language.LanguageServiceClient()

                            if isinstance(description, six.binary_type):
                                description = description.decode('utf-8')

                            try:
                                categories = client.classify_text(document).categories

                                for category in categories:
                                    content = url[
                                                  0] + '|CONTENT|' + lang + '|' + description + '|' + category.name + '|' + str(
                                        category.confidence)
                                    print("My content is ..", content)
                                    scrapped_data = content
                                    f.write(scrapped_data + '\n')


                            except Exception:
                                content = url[0] + '|CONTENT_UNCATEGORIZED|' + lang + '|' + description + '||'
                                print(content)
                                scrapped_data = content
                                f.write(scrapped_data + '\n')

                        if lang !='en':
                            print("language is not english running converter")
                            translator = Translator(from_lang=lang, to_lang="en")
                            translation = translator.translate(description)
                            classify(translation)

                        else:
                           content = url[0] + '|LANGUAGE_NOTSUPPORT|' + lang + '|' + description + '||'
                           print("content where language not supported", content)
                           scrapped_data = content
                           f.write(scrapped_data + '\n')

                else:
                    content = url[0] + '|Not_Scrapped||||'

            except KeyError as e:
                # url_e = url[0]+';URL_Error;'+e.response
                url_e = url[0] + '|KeyError|No_Content_In_DICT|||'
                print(url_e)
                # scrapped_data.append(url_e)
                scrapped_data = url_e
                f.write(scrapped_data + '\n')

    print('\n\n FINISHED SCRAPPING POST PROCESSING')

    f.close()
    print('*** Script completed ***')






















