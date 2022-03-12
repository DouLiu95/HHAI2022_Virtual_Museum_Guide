# Knowledge Graph Driven Virtual Museum Guide 
This project aims to use Dialogflow CX to build a knowledge graph driven virtual museum guide. 
You can try it on a web game demo. Or if you are interested, test it on your own machine is possible.


## Demo
A web demo can be found [here](https://douliu.itch.io/conversational-virtual-museum-guide?secret=SVwIuE2X8wDBNDXgNgp5Av2h6oo)
<img src="/resources/demo_web.jpg" alt="Demo" style="height: 1000px; width:1700px;"/>

## Requirement
- [Neo4j](https://neo4j.com/download/) 4.2+ (To store the knowledge base)
- ngrok (To make local python webhook project accessible by Dialogflow)
- [nginx](http://nginx.org/en/download.html) (To run the local virtual museum) 
- Python 3.7 virtual env with following packages to support webhook functions.
`pyahocorasick==1.4.2`,`py2neo==2021.1.1`,`flask`,`numpy`,`pandas`

## Instruction to run (on Windows 10)

### Neo4j

After you have installed Neo4j. Create a new project and database, then import the `resources/knowledge_graph/art_kg.csv`.

We collect this knowledge graph from [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page).

[Tutorial for import](https://neo4j.com/developer/guide-import-csv/)

Do not forget to change the config of knowledge base in `graph_database.py` as yours:

```python
# Change this setting of graph connection as yours

self.g = Graph(
            scheme="{your scheme}}",
            host="{your host}",
            port={your port},
            auth=("{your database}", "{your passport}"))
```

### Dialogflow Agent
*You could use my agent as long as my local server is up running so that the webhook will work normally.
If so, you could skip this part and the **ngrok** section below.*

The exported Dialogflow agent can be found in `resources/exported_agent_Artbot.blob`.

After importing the agent, to run it on the website, please go to `Dialogflow CX console -> Manage -> Integration -> Dialogflow Messenger -> Connect`. Now you could found the js code. Copy it and replace the Dialogflow Messenger code in `templates/index.html` with it.

```html
# replace following code with yours

<script src="https://www.gstatic.com/dialogflow-console/fast/messenger-cx/bootstrap.js?v=1"></script>
<df-messenger
  df-cx="true"
  location="us-east1"
  chat-title="Artbot"
  agent-id="6b21725c-c625-42dc-ad10-2ffe08a4f769"
  language-code="en"
></df-messenger>
```
Now you could start a local demo by runing `app.py` and open `http://127.0.0.1:5000/` in browser.

### nginx (optional)

*If you prefer test the Dialogflow agent without visiting the virtual museum, you may skip this part.* 

[Download nginx](http://nginx.org/en/download.html)

After downloading the nginx, copy the `resources/nginx/html` folder under this project to replace the `html` folder in your download. 

And replace following code in `resources/nginx/html/index.html` with yours.

```html
# replace following code with yours

<script src="https://www.gstatic.com/dialogflow-console/fast/messenger-cx/bootstrap.js?v=1"></script>
<df-messenger
  df-cx="true"
  location="us-east1"
  chat-title="Artbot"
  agent-id="6b21725c-c625-42dc-ad10-2ffe08a4f769"
  language-code="en"
></df-messenger>
```

Then run `nginx.exe` to start the server. And now you could access the virtual museum by enter `localhost` in you browser. 


### ngrok (optional)

*Skip this part if you use my Dialogflow messenger integration.*

ngrok can be found at `resources/ngrok/ngrok.exe`, you may need to register a free acount before using it.

After clone the project, run `app.py` to start serving flask app. Open the terminal and enter `ngrok` folder, then type 
```python
ngrok http 5000
``` 
to start the service. 
Then copy the https forwarding link, it is a URL looks like `https://xxxxx-xxxxx-xxxxx.ngrok.io`.

Go to `Dialogflow CX console -> Manage -> Webhooks`. Replace all the original URL with the link 'https://xxxxx-xxxxx-xxxxx.ngrok.io'.

For example, replace `https://6fcc-145-100-227-242.ngrok.io/questions` with `https://xxxxx-xxxxx-xxxxx.ngrok.io/quetions`.

## Instruction to talk with our agent
- Start the conversation by greeting!
- You could 
    - tell any exhibit in the virtual museum or painting works you like, such as `Tell me about King Caspar` (`King Caspar` is an exhibit in this virtual exhibition).
    - ask questions about a painting. Such as `Who painted the Night Watch?`
    - ask for recommendation (hope you like it!). Such as `Show me similar items like King Caspar.`
    
    
**Caution**: This agent is still at an early stage so it is not able to answer all kinds of questions or utterances. If you want to start over, you could refresh the website or just say "Hi".

Below is the list of exhibits in the virtual museum you could ask to the agent, and the agent will be happy to tell you some background stories of these exhibits.
```text
Two moors
King Caspar
Don Miguel de Castro, Emissary of Congo
Diego Bemba, a Servant of Don Miguel de Castro
Pedro Sunda, a Servant of Don Miguel de Castro
Map of Paranambucae
Portrait of a Black Woman
Portrait of a Man
Man in a Turban
Head of a Boy in a Turban
Doritos
The New Utopia Begins Here: Hermina Huiswoud
The Unspoken Truth
Ilona
Head of a Boy
The Market in Dam Square
```


## License

Distributed under the Apache 2.0 License. See [LICENSE](https://github.com/LDLucien/dfcx_virtual_museum_guide/blob/master/LICENSE) for more information.

