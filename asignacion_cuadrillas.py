import sys
#importamos el modulo cplex
import cplex
from recordclass import recordclass

TOLERANCE =10e-6 
Orden = recordclass('Orden', 'id beneficio cant_trab')

class InstanciaAsignacionCuadrillas:
    def __init__(self):
        self.cantidad_trabajadores = 0
        self.cantidad_ordenes = 0
        self.ordenes = []
        self.conflictos_trabajadores = []
        self.ordenes_correlativas = []
        self.ordenes_conflictivas = []
        self.ordenes_repetitivas = []
        
    def leer_datos(self,nombre_archivo):

        # Se abre el archivo
        f = open(nombre_archivo)

        # Lectura cantidad de trabajadores
        self.cantidad_trabajadores = int(f.readline())
        
        # Lectura cantidad de ordenes
        self.cantidad_ordenes = int(f.readline())
        
        # Lectura de las ordenes
        self.ordenes = []
        for i in range(self.cantidad_ordenes):
            linea = f.readline().rstrip().split(' ')
            self.ordenes.append(Orden(linea[0],linea[1],linea[2]))
        
        # Lectura cantidad de conflictos entre los trabajadores
        cantidad_conflictos_trabajadores = int(f.readline())
        
        # Lectura conflictos entre los trabajadores
        self.conflictos_trabajadores = []
        for i in range(cantidad_conflictos_trabajadores):
            linea = f.readline().split(' ')
            self.conflictos_trabajadores.append(list(map(int,linea)))
            
        # Lectura cantidad de ordenes correlativas
        cantidad_ordenes_correlativas = int(f.readline())
        
        # Lectura ordenes correlativas
        self.ordenes_correlativas = []
        for i in range(cantidad_ordenes_correlativas):
            linea = f.readline().split(' ')
            self.ordenes_correlativas.append(list(map(int,linea)))
            
        # Lectura cantidad de ordenes conflictivas
        cantidad_ordenes_conflictivas = int(f.readline())
        
        # Lectura ordenes conflictivas
        self.ordenes_conflictivas = []
        for i in range(cantidad_ordenes_conflictivas):
            linea = f.readline().split(' ')
            self.ordenes_conflictivas.append(list(map(int,linea)))
        
        # Lectura cantidad de ordenes repetitivas
        cantidad_ordenes_repetitivas = int(f.readline())
        
        # Lectura ordenes repetitivas
        self.ordenes_repetitivas = []
        for i in range(cantidad_ordenes_repetitivas):
            linea = f.readline().split(' ')
            self.ordenes_repetitivas.append(list(map(int,linea)))
        
        # Se cierra el archivo de entrada
        f.close()


def cargar_instancia():
    # El 1er parametro es el nombre del archivo de entrada 	
    nombre_archivo = sys.argv[1].strip()
    # Crea la instancia vacia
    instancia = InstanciaAsignacionCuadrillas()
    # Llena la instancia con los datos del archivo de entrada 
    instancia.leer_datos(nombre_archivo)
    return instancia

def agregar_variables(prob, instancia):
    # Definir y agregar las variables:
	# metodo 'add' de 'variables', con parametros:
	# obj: costos de la funcion objetivo
	# lb: cotas inferiores
    # ub: cotas superiores
    # types: tipo de las variables
    # names: nombre (como van a aparecer en el archivo .lp)
	
    T = instancia.cantidad_trabajadores
    O = instancia.cantidad_ordenes
    K = 6 # Días hábiles
    L = 5 # Turnos por día 

    # Llenar coef\_funcion\_objetivo
    coeficientes_funcion_objetivo = []

    # Poner nombre a las variables
    nombres = []
    tipos = []

    
    # Variables delta_ij
    for i in range(T):
        for j in range(O):
            coeficientes_funcion_objetivo.append(0)  # 0 porque no esta en la funcion objetivo
            nombres.append(f"delta_{i}_{j}")
            tipos.append('B')

    # Variables alfa_jkl
    for j in range(O):
        for k in range(K):
            for l in range(L):
                coeficientes_funcion_objetivo.append(instancia.ordenes[j].beneficio)  
                nombres.append(f"alfa_{j}_{k}_{l}")
                tipos.append('B')

    # Variables beta_ijkl
    for i in range(T):
        for j in range(O):
            for k in range(K):
                for l in range(L):
                    coeficientes_funcion_objetivo.append(0)  # 0 porque no esta en la funcion objetivo
                    nombres.append(f"beta_{i}_{j}_{k}_{l}")
                    tipos.append('B')

    # Variables omega_ik
    for i in range(T):
        for k in range(K):
            coeficientes_funcion_objetivo.append(0)  # 0 porque no esta en la funcion objetivo
            nombres.append(f"omega_{i}_{k}")
            tipos.append('B')
    
    # Variables gamma_i^n
    for i in range(T):
        for n in range(1, 4):
            coeficientes_funcion_objetivo.append(0)  # 0 porque no esta en la funcion objetivo
            nombres.append(f"gamma_{i}_{n}")
            tipos.append('B')

    # Variables c_i_n
    for i in range(T):
        for n in range(1,5): 
            coeficientes_funcion_objetivo.append(-1000 * (n == 1) - 1200 * (n == 2) - 1400 * (n == 3) - 1500 * (n == 4))  
            nombres.append(f"c_{i}_{n}")
            tipos.append('I')

 
    lb = [0] * (len(coeficientes_funcion_objetivo)) 
    ub = [1] * (len(coeficientes_funcion_objetivo)-4*T)
    ub.extend([O] * (4 * T))

    
    # Agregar las variables
    prob.variables.add(obj=coeficientes_funcion_objetivo, lb=lb, ub=ub, types=tipos, names=nombres)

def agregar_restricciones(prob, instancia):
    # Agregar las restricciones ax <= (>= ==) b:
	# funcion 'add' de 'linear_constraints' con parametros:
	# lin_expr: lista de listas de [ind,val] de a
    # sense: lista de 'L', 'G' o 'E'
    # rhs: lista de los b
    # names: nombre (como van a aparecer en el archivo .lp)
	
    # Notar que cplex espera "una matriz de restricciones", es decir, una
    # lista de restricciones del tipo ax <= b, [ax <= b]. Por lo tanto, aun cuando
    # agreguemos una unica restriccion, tenemos que hacerlo como una lista de un unico
    # elemento.

    # Restriccion generica
    indices = ...
    valores = ...
    fila = [indices,valores]
    prob.linear_constraints.add(lin_expr=[fila], senses=[...], rhs=[...], names=[...])

def armar_lp(prob, instancia):

    # Agregar las variables
    agregar_variables(prob, instancia)
   
    # Agregar las restricciones 
    agregar_restricciones(prob, instancia)

    # Setear el sentido del problema
    prob.objective.set_sense(prob.objective.sense.....)

    # Escribir el lp a archivo
    prob.write('asignacionCuadrillas.lp')

def resolver_lp(prob):
    
    # Definir los parametros del solver
    prob.parameters....
       
    # Resolver el lp
    prob.solve()

def mostrar_solucion(prob,instancia):
    # Obtener informacion de la solucion a traves de 'solution'
    
    # Tomar el estado de la resolucion
    status = prob.solution.get_status_string(status_code = prob.solution.get_status())
    
    # Tomar el valor del funcional
    valor_obj = prob.solution.get_objective_value()
    
    print('Funcion objetivo: ',valor_obj,'(' + str(status) + ')')
    
    # Tomar los valores de las variables
    x  = prob.solution.get_values()
    # Mostrar las variables con valor positivo (mayor que una tolerancia)
    .....

def main():
    
    # Lectura de datos desde el archivo de entrada
    instancia = cargar_instancia()
    
    # Definicion del problema de Cplex
    prob = cplex.Cplex()
    
    # Definicion del modelo
    armar_lp(prob,instancia)

    # Resolucion del modelo
    resolver_lp(prob)

    # Obtencion de la solucion
    mostrar_solucion(prob,instancia)

if __name__ == '__main__':
    main()
