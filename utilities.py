import urllib
import json


__author__='papalinis - Simone Papalini - papalini.simone.an@gmail.com'


class Utilities:
    # TODO DOCSTRINGS
    """

    """
    def __init__(self, lang):
        self.lang = lang
        self.jsonpedia_call_format = "?&procs=Extractors,Structure"
        self.jsonpedia_section_format = "?filter=@type:section&procs=Extractors,Structure"
        self.jsonpedia_tables_format = "?filter=@type:table&procs=Extractors,Structure"
        self.call_format_sparql = "&format=application%2Fsparql-results%2Bjson&debug=on"
        self.jsonpedia_base_url = "http://jsonpedia.org/annotate/resource/json/"
        self.jsonpedia_lan = lang + ":"
        self.dbpedia = None
        self.dbpedia_sparql_url = self.dbpedia_selection()
        self.res_lost_jsonpedia = 0

    def dbpedia_selection(self):
        """

        :return:
        """
        if self.lang != "en":
            self.dbpedia = self.lang + ".dbpedia.org"
        else:
            self.dbpedia = "dbpedia.org"
        return "http://" + self.dbpedia + "/sparql?default-graph-uri=&query="

    def url_composer(self, query, service):
        """
        This function is used to compose a url to call some std services used by the selector,
        such as sparql endpoints or as jsonpedia rest service.
        Before returning the url composed, the method replaces
        :param query: is the string used in some rest calls. For a jsonpedia service is typically the resource name.
        :param service: type of service you request (jsonpedia, dbpedia sparql endpoint..)
        :return url: the url composed
        """
        # TODO conditions for dbpedia/jsonpedia services
        query = urllib.quote_plus(query)
        if service == 'dbpedia':
            url = self.dbpedia_sparql_url + query + self.call_format_sparql
            return url
        elif service == 'jsonpedia':
            url = self.jsonpedia_base_url + self.jsonpedia_lan + query + self.jsonpedia_call_format
            return url
        elif service == 'jsonpedia_tables':
            url = self.jsonpedia_base_url + self.jsonpedia_lan + query + self.jsonpedia_tables_format
            return url
        elif service == 'jsonpedia_sections':
            url = self.jsonpedia_base_url + self.jsonpedia_lan + query + self.jsonpedia_section_format
            return url
        else:
            return "ERROR"

    def json_answer_getter(self, url_passed):
        """
        json_answer_getter is a method used to call a REST service and to parse the answer in json.
        It returns a json parsed answer if everything is ok
        :param url_passed: type string,is the url to reach for a rest service
        :return json_parsed: the method returns the answer parsed in json
        """
        try:
            call = urllib.urlopen(url_passed)
            answer = call.read()
            json_parsed = json.loads(answer)
            return json_parsed
        except IOError:
            print ("Try, again, some problems due to Internet connection, url: "+url_passed)
            return "Internet problems"
        except ValueError:
            print ("Not a JSON object.")
            return "ValueE"
        except:
            print "Exception with url:" + str(url_passed)
            return "GeneralE"

    def json_object_getter(self,resource, struct='jsonpedia'):
        """

        :param resource:
        :param struct:
        :return:
        """
        jsonpedia_url = self.url_composer(resource, struct)
        json_object_state = 'try'
        while json_object_state == 'try':
            try:
                json_answer = self.json_answer_getter(jsonpedia_url)
                if type(json_answer) != str:
                    json_object_state = self.test_json_result(json_answer)
            except:
                print("Error during json_object_getter")
        print(json_object_state)
        return json_answer


    def test_json_result(self, json_obj):
        if 'message' in json_obj.keys():
            # TODO think about the possibility of write down problems encountered
            message = json_obj['message']
            if message == u'Invalid page metadata.':
                self.res_lost_jsonpedia += 1
                return 'Invalid page metadata'

            elif message == u'Expected DocumentElement found ParameterElement':
                self.res_lost_jsonpedia += 1
                return 'Expected DocumentElement found ParameterElement'

            elif message == u'Expected DocumentElement found ListItem':
                self.res_lost_jsonpedia += 1
                return 'Expected DocumentElement found ListItem'

            elif message == u'Expected DocumentElement found TableCell':
                self.res_lost_jsonpedia += 1
                return 'Expected DocumentElement found TableCell'

            elif len(json_obj) == 3:
                print "Problems related to JSONpedia service :" + str(json_obj) + " - RETRYING"
                return 'try'
        else:
            return 'ok'
