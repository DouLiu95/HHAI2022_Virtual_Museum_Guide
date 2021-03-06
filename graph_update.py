
def draw_graph(uri1='', uri2='', new_query = ''):
    html = '''<html>
    <head>
        <title>Neovis.js Simple Example</title>
        <style type="text/css">
            html, body {
                font: 16pt arial;
            }
    
            #viz {
                width: 900px;
                height: 700px;
                border: 1px solid lightgray;
                font: 22pt arial;
            }
    
        </style>
    
        <!-- FIXME: load from dist -->
        <script src="https://rawgit.com/neo4j-contrib/neovis.js/master/dist/neovis.js"></script>
    
    
        <script
                src="https://code.jquery.com/jquery-3.2.1.min.js"
                integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4="
                crossorigin="anonymous"></script>
    
        <script type="text/javascript">
            // define config car
            // instantiate nodevis object
            // draw
    
            var viz;
    
            function draw() {
                var config = {
                    container_id: "viz",
                    server_url: "bolt://localhost:7687",
                    server_user: "neo4j",
                    server_password: "000000",
                    labels: {
                        //"Character": "name",
                        "Paintings": {
                            "caption": "name",
                            "size": "sitelink"
                            // "community": "community"
                            //"sizeCypher": "MATCH (n) WHERE id(n) = {id} MATCH (n)-[r]-() RETURN sum(r.weight) AS c"
                        },
                        "Person": {
                            "caption":"name",
                            "size": "sitelink"
                        },
                        "Material": {
                            "caption":"name",
                            "size": "sitelink"
                        },
                        "Genre":{
                            "caption":"name",
                            "size": "sitelink"
                        },
                        "Keyword":{
                            "caption":"name",
                            "size": "sitelink"
                        },
                        "Movement":{
                            "caption":"name",
                            "size": "sitelink"
                        },
                        "Country":{
                            "caption":"name",
                            "size": "sitelink"
                        }
                        ,
                        "Exhibition":{
                            "caption":"name",
                            "size": "sitelink"
                        },
    
                        "Collection":{
                            "caption":"name",
                            "size": "sitelink"
                        },
                        "City":{
                            "caption":"name",
                            "size": "sitelink"
                        }
    
                    },
                    relationships: {
                        "belongsto_GENRE": {
                            // "thickness": "weight",
                            "caption": false
                        },
                        "belongsto_MOVEMENT":{
                            // "thickness":"weight",
                            "caption":false
                        },
                        "has_CREATOR":{
                            // "thickness":"weight",
                            "caption":false
                        },
                        "has_KEYWORD":{
                            // "thickness":"weight",
                            "caption":false
                        },
                        "in_CITY":{
                            // "thickness":"weight",
                            "caption":false
                        },
                        "in_COLLECTION":{
                            // "thickness":"weight",
                            "caption":false
                        },
                        "in_COUNTRY":{
                            // "thickness":"weight",
                            "caption":false
                        },
                        "in_EXHIBITION":{
                            // "thickness":"weight",
                            "caption":false
                        },
                        "on_MATERIAL":{
                            // "thickness":"weight",
                            "caption":false
                        }
                    },
                    initial_cypher:
                };
    
                viz = new NeoVis.default(config);
                viz.render();
                console.log(viz);
    
            }
        </script>
    </head>
    <body onload="draw()">
    <div id="viz"></div>
    
    
    Cypher query: <textarea rows="4" cols=50 id="cypher"></textarea><br>
    <input type="submit" value="Submit" id="reload">
    <input type="submit" value="Stabilize" id="stabilize">
    
    
    </body>
    
    <script>
        $("#reload").click(function() {
    
            var cypher = $("#cypher").val();
    
            if (cypher.length > 3) {
                viz.renderWithCypher(cypher);
            } else {
                console.log("reload");
                viz.reload();
    
            }
    
        });
    
        $("#stabilize").click(function() {
            viz.stabilize();
        })
    
    </script>
    </html>
    '''
    if new_query == '':
        new_query = "MATCH (a {uri: '"+uri1+"'}), (b {uri: '"+uri2+"'}), p = (a)-[r:belongsto_GENRE|has_CREATOR|belongsto_MOVEMENT|has_KEYWORD|on_MATERIAL|in_COLLECTION|in_EXHIBITION1*1..3]-(b) RETURN p"  # test usage

        new_html = html.replace("initial_cypher:", "initial_cypher: \"" + new_query + "\"")
        # print(new_html)
        with open("templates/neovis.html", "w") as file:
            file.write(new_html)
        return new_query
    else:
        new_html = html.replace("initial_cypher:", "initial_cypher: \"" + new_query + "\"")
        # print(new_html)
        with open("templates/neovis.html", "w") as file:
            file.write(new_html)
        return new_query
# draw_graph("MATCH (a:Paintings {name: 'The Night Watch'}), (b:Paintings {name: 'Two moors'}), p = shortestPath((a)-[*]-(b)) RETURN p")