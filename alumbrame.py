#import mariadb
import mysql.connector
import glob
import jsonpickle
from numpy import loadtxt
import sys
from datetime import datetime
now = datetime.now()

AGENT = 0
IMPORTANT =  1
RESOLVED = 2
CONFIRMED = 3

# Dictionaries for Mantis values
d_status = { }
d_status[10] = "👶 Nueva"
d_status[20] = "📬 SNMD"
d_status[30] = "👁 En proceso"
d_status[40] = "👍 Confirmada"
d_status[50] = "🎯 Asignada"
d_status[60] = "📆 Programada"
d_status[80] = "✅ Resuelta"
d_status[90] = "🔒 Cerrada"

d_priority = { }
d_priority[10] = "Ninguna"
d_priority[20] = "Baja"
d_priority[30] = "Normal"
d_priority[40] = "Alta"
d_priority[50] = "Urgente"
d_priority[60] = "Inmediata"

d_category = { }
d_category["10_Error"] = "Error"
d_category["20_Tarea"] = "Tarea"
d_category["30_Mejora"] = "Mejora"
d_category["40_Consulta"] = "Consulta"
d_category["45_Formación"] = "Formación"
d_category["80_Credenciales"] = "Credenciales"
d_category["90_Carga"] = "Carga"
d_category["95_Extraccion"] = "Extracción"

d_memory = { } # Used to store historical values for graphs
d_memory["total_asignadas"] = 0
d_memory["total_enproceso"] = 0
d_memory["total_snmd"] = 0
d_memory["total_confirmadas"] = 0

# Creates a table in the specified md file following certain rules
def makeTable(md, rules, userid):
    if(rules == AGENT):
        md.write("|Ticket|Resumen|Estado|Prioridad|PF|Categoría|Módulo|Retraso|\n")
    else:
        md.write("|Ticket|Resumen|Agente|Estado|Prioridad|PF|Categoría|Módulo|Retraso|\n")
    md.write("|-|\n")
    for ticket in ticketList:
        if((rules == AGENT and ticket.handler == userid)
        or (rules == IMPORTANT and ticket.pf != "" and float(ticket.pf) < 1)
        or (rules == RESOLVED and ticket.status == 80)):
            md.write("|")
            md.write("[" + str(ticket.id) + "](http://ticket.san.gva.es/mantisbt/view.php?id="  + str(ticket.id) + ")")
            md.write("|")
            md.write(ticket.title)
            if(rules != AGENT):
                md.write("|")
                md.write("[" + ticket.realName + "](mantis-" + ticket.handler + ".md)")
            md.write("|")
            md.write(d_status[ticket.status])
            md.write("|")
            md.write(d_priority[ticket.priority])
            md.write("|")
            if(ticket.pf != None):
                md.write(str(ticket.pf))
            md.write("|")
            md.write(d_category[ticket.category])
            md.write("|")
            md.write(ticket.mod)
            md.write("|")
            if(ticket.delay != 0):
                if(ticket.delay == 1):
                    md.write("1 día")
                elif(ticket.delay > 7):
                    md.write(str(ticket.delay) + " días 🚩")
                else:
                    md.write(str(ticket.delay) + " días")
            md.write("|\n")

# Create md file
def makePage(userid, name):

    # Index
    if(userid == "index"):
        md = open("index.md", "w", encoding="utf-8")
        md.write("# " + name)
        md.write("\n")
        md.write("Bienvenid@ a **AlumbraMe!**, la base de conocimiento colaborativa de Soporte Alumbra.")
        md.write("\n\n \n\n")
        
        # Soporte News
        md.write("|🛸 Soporte News|\n")
        md.write("|-|\n")
        f = open("news.txt", encoding="utf-8")
        while True:
            line = f.readline()
            if not line:
                break
            md.write("|" + line)
        f.close()
        md.write("\n\n")
        md.write('![](index-1.gif "Inicio")')
        md.close()
    
    # Monitoring
    elif(userid == "monitorizacion"):
        md = open("monitorizacion.md", "w", encoding="utf-8")
        md.write("# " + name)
        md.write("\n\n")

        # Queue links
        md.write("[**👩‍💻 Andrea**](mantis-sanchez_and.md) - Resolución de incidencias, extracciones\n")
        md.write("[**👩‍💻 Karen**](mantis-maya_kar.md) - Resolución de incidencias, cargas\n")
        md.write("[**👩‍💻 Sheila**](mantis-membrado_she.md) - Gestión del correo, atención a usuarios\n")
        md.write("[**👩‍💻 Vicenta**](mantis-sanchis_vic.md) - Gestión de seguridad\n")
        md.write("[**👨‍💻 Jose**](mantis-juan_jos.md) - Resolución de incidencias, coordinación del equipo\n")
        md.write("\n\n \n\n")
        
        # High priority
        md.write("🚩 **Incidencias de mayor prioridad**. <small>Errores de datos, urgentes e inmediatas.</small>\n\n")
        makeTable(md, IMPORTANT, userid)

        # Resolved
        md.write("✅ **Incidencias resueltas**. <small>Incidencias resueltas por el equipo de analistas y reasignadas a Soporte a la espera de ser confirmadas con el usuario.</small>\n\n")
        makeTable(md, RESOLVED, userid)
        md.write("<small>Último refresco: " + str(now.strftime("%d/%m/%Y %H:%M:%S")) + "</small>")
        md.close()

    # Agent
    else:
        md = open("mantis-" + userid + ".md","w",encoding="utf-8")
        md.write("# " + name)
        md.write("\n")
        makeTable(md, AGENT, userid)
        md.write("<small>Último refresco: " + str(now.strftime("%d/%m/%Y %H:%M:%S")) + "</small>")
        md.close()

# Ticket array
class ticket():
    def __init__(self, id=None, title=None, status=None, priority=None, pf=None, category=None, mod=None, delay=None, handler=None, realName=None):
        self.id = id
        self.title = title
        self.status = status
        self.priority = priority
        self.pf = pf
        self.category = category
        self.mod = mod
        self.delay = delay
        self.handler = handler
        self.realName = realName
ticketList = []

# Data object
class data():
    def __init__(self):
        self.d_status { }
        self.d_category { }
        self.d_agent { }

# Database connection
#conn = mariadb.connect(user="us_lectura", password="us_lectura", host="172.17.8.96", port=3306, database='bugtracker')
conn = mysql.connector.connect(host="mysql.fractalmonkey.xyz", user="seikken", passwd="ovislink1", database="alumbra_mantis ") 

# SQL select
# pf: 91 / 1
# módulo: 11 / 2
cur = conn.cursor()
cur.execute("""
SELECT distinct bug.id as id,
       bug.summary as summary,
       bug.status as status,
       bug.priority as priority,
       pf.value as pf,
       cat.name as cat,
       module.value as module,
       DATEDIFF(CURDATE(), FROM_UNIXTIME(bug.date_submitted, '%y-%m-%d')),
       user.username as handler,
       user.realname as realName
FROM mantis_bug_table bug
LEFT JOIN mantis_user_table user ON bug.handler_id = user.id
LEFT JOIN mantis_category_table cat ON bug.category_id = cat.id
LEFT JOIN mantis_custom_field_string_table pf on bug.id = pf.bug_id AND pf.field_id = 1
LEFT JOIN mantis_custom_field_string_table module on bug.id = module.bug_id AND module.field_id = 2
WHERE user.username IN ('maya_kar', 'juan_jos', 'sanchez_and', 'sanchis_vic', 'membrado_she', 'soporte_alumbra')
ORDER BY bug.status desc
""") 

# Store query data into ticket array
for(id, summary, status, priority, pf, cat, module, delay, handler, realName) in cur:
    ticketList.append(ticket(id, summary, status, priority, pf, cat, module, delay, handler, realName))

# Close database connection
conn.close()

# Create md files
makePage("sanchez_and", "Andrea")
makePage("membrado_she", "Sheila")
makePage("juan_jos", "Jose")
makePage("sanchis_vic", "Vicenta")
makePage("maya_kar", "Karen")
makePage("index", "Inicio")
makePage("monitorizacion", "Monitorización")