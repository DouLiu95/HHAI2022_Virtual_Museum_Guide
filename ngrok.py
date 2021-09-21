from pyngrok import ngrok,conf
# Open a HTTP tunnel on the default port 80
# <NgrokTunnel: "http://<public_sub>.ngrok.io" -> "http://localhost:80">
def log_event_callback(log):
    print(str(log))

conf.get_default().log_event_callback = log_event_callback
http_tunnel = ngrok.connect("file:///C:/Users/LDLuc/Pictures/final_thesis/path/",bind_tls=True)
tunnels = ngrok.get_tunnels()
print(tunnels)
# The NgrokTunnel returned from methods like connect(),
# get_tunnels(), etc. contains the public URL
# ngrok.disconnect(ngrok_tunnel.public_url)
