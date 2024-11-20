import sys
import tkinter as tk
from tkinter import scrolledtext
import ply.lex as lex
import ply.yacc as yacc

# Definir tokens.
tokens = (
    'LLAVE_IZQ',
    'LLAVE_DER',
    'DOSPUNTOS',
    'PARIZQ',
    'PARDER',
    'ACCION',
    'SENSOR',
    'OPERADOR',
    'VALOR',
    'SEP'
)

# Expresiones regulares para cada token.
t_LLAVE_IZQ = r'\{'
t_LLAVE_DER = r'\}'
t_DOSPUNTOS = r':'
t_PARIZQ = r'\('
t_PARDER = r'\)'
t_ACCION = r'regar|encender_luces|encender_ventilacion|ajustar_ph|fertilizar|apagar_luces|apagar_ventilacion|inyeccion_CO2|apagar_fertilizado'
t_SENSOR = r'temperatura|luzNatural|humedad|ph|CO2'
t_OPERADOR = r'<|>|<=|>=|=|!='
t_VALOR = r'\d+'
t_SEP = r'\|'

# Ignorar espacios y nuevas líneas.
t_ignore = ' \t\n'

# Manejo de errores léxicos
def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

# Construir el analizador léxico.
lexer = lex.lex()

# Diccionario para validar las combinaciones acción-sensor.
accion_sensor_permitidos = {
    'regar': ['humedad'],
    'encender_luces': ['luzNatural'],
    'encender_ventilacion': ['temperatura', 'CO2'],
    'ajustar_ph': ['ph'],
    'apagar_luces': ['luzNatural'],
    'apagar_ventilacion': ['temperatura', 'CO2'],
    'inyeccion_CO2': ['CO2'],
    #
    'fertilizar': [''],
    'apagar_fertilizado': ['']
}

# Regla inicial.
start = 'instrucciones'




# Definir la gramática en PLY.
def p_instrucciones(p):
    '''instrucciones : LLAVE_IZQ ACCION PARIZQ PARDER DOSPUNTOS condicion LLAVE_DER'''
    p[0] = f"{p[2]} {p[6]}"

      # Validar si el sensor es válido para la acción.
    sensor = p[6].split()[0]
    if sensor not in accion_sensor_permitidos[p[2]]:
        print(f"Error: La acción '{p[2]}' no puede ser usada con el sensor '{sensor}'")
    else:
        p[0] = f"{p[2]} {p[6]}"
        print("La instrucción es:", p[2], "con la condición:", p[6])
    

def p_condicion(p):
    '''condicion : SENSOR OPERADOR VALOR'''
    p[0] = f"{p[1]} {p[2]} {p[3]}"

# Definir instruccion con horario.
def p_instruccion_corta(p):
    '''instrucciones : LLAVE_IZQ ACCION PARIZQ PARDER DOSPUNTOS horario LLAVE_DER'''
    p[0] = f"{p[2]}"
    print("La instrucción es:", p[2], "en el horario:", p[6])

def p_horario(p):
    '''horario : VALOR SEP VALOR'''
    p[0] = f"{p[1]}|{p[3]}"

def p_error(p):
    if p:
        print(f"Error de sintaxis en '{p.value}' en la línea {p.lineno}")
    else:
        print("Se esperaba '}'.")

# Construir el analizador sintáctico.
parser = yacc.yacc()


# 3. Clase para redirigir la salida de la terminal
class RedirectText:
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END)  # Desplaza automáticamente hacia el final del texto

    def flush(self):
        pass  # No es necesario para esta implementación

# 4. Interfaz gráfica
root = tk.Tk()
root.title("Interpretador de Código")
root.geometry("800x600")
root.config(bg="green")

entrada = tk.Entry(root)
entrada.config(width=80)
entrada.pack(pady=10)

salida_terminal = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=30, width=90, state=tk.NORMAL)
salida_terminal.pack(padx=10, pady=10)
salida_terminal.config(bg="#666666", fg="white")

# Redirigir la salida estándar y de errores a `salida_terminal`
stdout_redirigido = RedirectText(salida_terminal)
sys.stdout = stdout_redirigido
sys.stderr = stdout_redirigido

# Función para enviar el comando
def enviar_comando():
    intrucciones= []
    ultimaLlaveCierre = 0
    codigo = entrada.get()
    if codigo.strip():
        for i in range(len(codigo)):
            if codigo[i] == '}':
                intrucciones.append(codigo[ultimaLlaveCierre:i+1])
                ultimaLlaveCierre = i+1

        if len(intrucciones) == 0:
            parser.parse(codigo)
        else:
            for instruccion in intrucciones:
                parser.parse(instruccion)
        if ultimaLlaveCierre < len(codigo) and len(intrucciones) != 0:
            parser.parse(codigo[ultimaLlaveCierre:])
        
       

boton_interpretar = tk.Button(root, text="Interpretar", command=enviar_comando)
boton_interpretar.pack(pady=10)

root.mainloop()