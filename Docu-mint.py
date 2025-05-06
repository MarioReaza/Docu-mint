import os
import mimetypes

def es_archivo_de_texto(ruta_archivo, extensiones_excluidas=None):
    """
    Determina si un archivo es de texto basado en su extensión y tipo MIME. Excluye archivos con extensiones específicas si se proporcionan.
    """
    if not mimetypes.inited:
        mimetypes.init()
    
    extension = os.path.splitext(ruta_archivo)[1].lower()
    
    if extensiones_excluidas and extension in extensiones_excluidas:
        return False
    
    extensiones_texto = {
        '.txt', '.md', '.py', '.js', '.html', '.css', '.java', '.c', '.cpp', 
        '.h', '.cs', '.php', '.rb', '.pl', '.sh', '.bat', '.ps1', '.sql', 
        '.xml', '.json', '.yaml', '.yml', '.ini', '.cfg', '.conf', '.gitignore',
        '.htaccess', '.csv', '.log', '.ts', '.jsx', '.tsx', '.vue', '.go', 
        '.rs', '.swift', '.kt', '.scala', '.dart', '.lua', '.R', '.m', '.tex',
        '.rst', '.diff', '.patch', '.toml', '.env'
    }
    
    if extension in extensiones_texto:
        return True
    
    tipo_mime, _ = mimetypes.guess_type(ruta_archivo)
    
    if tipo_mime and tipo_mime.startswith('text/'):
        return True
    
    return False

def calcular_profundidad(directorio_base, directorio_actual):
    """
    Calcula la profundidad entre el directorio base y el directorio actual.
    """
    directorio_base = os.path.normpath(directorio_base)
    directorio_actual = os.path.normpath(directorio_actual)
    
    if directorio_base == directorio_actual:
        return 0
        
    ruta_relativa = os.path.relpath(directorio_actual, directorio_base)
    
    if ruta_relativa == '.':
        return 0
        
    return ruta_relativa.count(os.sep) + 1

def generar_cadena_de_archivos(directorio, profundidad_max=None, directorios_excluidos=None, extensiones_excluidas=None):
    """
    Genera una cadena con información sobre los archivos en un directorio,
    incluyendo el contenido solo para archivos de texto, hasta una profundidad máxima.
    
    Args:
        directorio: Ruta del directorio a analizar
        profundidad_max: Profundidad máxima de subdirectorios a explorar (None = sin límite)
        directorios_excluidos: Lista de nombres de directorios a excluir
        extensiones_excluidas: Lista de extensiones de archivo a excluir (incluir el punto, ej: ['.json'])
    """
    resultado = []
    
    if directorios_excluidos is None:
        directorios_excluidos = []
        
    if extensiones_excluidas is None:
        extensiones_excluidas = []
    
    if not os.path.exists(directorio):
        return f"Error: El directorio '{directorio}' no existe."
    
    for root, dirs, files in os.walk(directorio):
        dirs_copy = dirs.copy()
        for d in dirs_copy:
            if d in directorios_excluidos:
                dirs.remove(d)
                resultado.append(f"\n--- Directorio excluido: {os.path.join(root, d)} ---\n")
        
        profundidad_actual = calcular_profundidad(directorio, root)
        
        if profundidad_max is not None and profundidad_actual >= profundidad_max:
            dirs.clear()  # Esto evita que os.walk descienda más
        
        archivos_filtrados = []
        archivos_excluidos = 0
        
        for f in files:
            extension = os.path.splitext(f)[1].lower()
            if extension in extensiones_excluidas:
                archivos_excluidos += 1
                continue
            archivos_filtrados.append(f)
        
        if archivos_filtrados or archivos_excluidos > 0:
            encabezado = f"\n--- Directorio: {root} (Profundidad: {profundidad_actual}) ---\n"
            if archivos_excluidos > 0:
                encabezado += f"--- Se han excluido {archivos_excluidos} archivo(s) por extensión ---\n"
            resultado.append(encabezado)
        
        for f in archivos_filtrados:
            ruta_completa = os.path.join(root, f)
            
            if es_archivo_de_texto(ruta_completa, extensiones_excluidas):
                try:
                    with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as archivo:
                        contenido = archivo.read()
                    resultado.append(f'Nombre: {f}, Ruta: {ruta_completa}\n"{contenido}"\n')
                except Exception as e:
                    resultado.append(f'Nombre: {f}, Ruta: {ruta_completa}\n**No se pudo leer el archivo**: {e}\n')
            else:
                resultado.append(f'Nombre: {f}, Ruta: {ruta_completa}\n**Archivo no texto - No se muestra contenido**\n')
    
    return "\n".join(resultado)

def main():
    directorio_base = input("Introduce la ruta del directorio a analizar: ")
    
    profundidad_input = input("Introduce la profundidad máxima de subdirectorios a explorar (deja en blanco para sin límite): ")
    
    profundidad_max = None
    if profundidad_input.strip():
        try:
            profundidad_max = int(profundidad_input)
            if profundidad_max < 0:
                print("La profundidad debe ser un número no negativo. Se usará sin límite.")
                profundidad_max = None
        except ValueError:
            print("Entrada inválida para la profundidad. Se usará sin límite.")
    
    directorios_comunes_excluir = ['node_modules', 'venv', '.venv', '__pycache__', 'dist', 'build', '.git']
    
    excluir_comunes = input(f"¿Quieres excluir directorios comunes como {', '.join(directorios_comunes_excluir)}? (s/n): ").strip().lower()
    
    directorios_excluidos = []
    if excluir_comunes.startswith('s'):
        directorios_excluidos.extend(directorios_comunes_excluir)
        print(f"Se excluirán los siguientes directorios: {', '.join(directorios_excluidos)}")
    
    excluir_adicionales = input("¿Quieres excluir directorios adicionales? (s/n): ").strip().lower()
    if excluir_adicionales.startswith('s'):
        dirs_adicionales = input("Introduce los nombres de los directorios a excluir separados por comas: ")
        if dirs_adicionales.strip():
            directorios_excluidos.extend([d.strip() for d in dirs_adicionales.split(',')])
    
    extension_input = input("¿Quieres excluir tipos de archivos por extensión? (s/n): ").strip().lower()
    
    extensiones_excluidas = []
    if extension_input.startswith('s'):
        ext_input = input("Introduce las extensiones a excluir separadas por comas (ejemplo: .json, .lock): ")
        if ext_input.strip():
            for ext in ext_input.split(','):
                ext = ext.strip().lower()
                if not ext.startswith('.'):
                    ext = '.' + ext
                extensiones_excluidas.append(ext)
            print(f"Se excluirán archivos con las siguientes extensiones: {', '.join(extensiones_excluidas)}")
    
    print(f"Analizando archivos en: {directorio_base}" + 
          (f" (profundidad máxima: {profundidad_max})" if profundidad_max is not None else " (sin límite de profundidad)"))
    
    if directorios_excluidos:
        print(f"Excluyendo los siguientes directorios: {', '.join(directorios_excluidos)}")
    if extensiones_excluidas:
        print(f"Excluyendo archivos con las siguientes extensiones: {', '.join(extensiones_excluidas)}")
    
    texto_resultante = generar_cadena_de_archivos(directorio_base, profundidad_max, directorios_excluidos, extensiones_excluidas)
    
    archivo_salida = input("Introduce el nombre del archivo de salida (por defecto: resultado.txt): ")
    if not archivo_salida:
        archivo_salida = "resultado.txt"
    
    if not archivo_salida.lower().endswith('.txt'):
        archivo_salida += '.txt'
    
    with open(archivo_salida, "w", encoding="utf-8") as salida:
        salida.write(texto_resultante)
    
    print(f"El resultado ha sido guardado en '{archivo_salida}'.")

if __name__ == "__main__":
    main()
