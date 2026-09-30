"""
task_manager_ai_native.py
Versión corregida y refactorizada - Taller AI-Native Software Engineer

Mejoras principales introducidas:
1. Seguridad / Aislamiento: `list_tasks` solo devuelve las tareas del usuario especificado.
2. Sincronización de índices: Se implementó un mapeo de referencias para asegurar que
   el índice de la interfaz (relativo al usuario) modifique/elimine la tarea correcta
   en la lista global `tasks`.
3. Validaciones robustas: Se previenen títulos vacíos y conversiones fallidas de índices.
4. Manejo de excepciones claro: La GUI captura errores específicos y muestra alertas
   informativas al usuario mediante `messagebox`.
"""

import tkinter as tk
from tkinter import ttk, messagebox


# Estructura de almacenamiento global de tareas
tasks = []


# ==============================================================================
# LÓGICA DE NEGOCIO Y OPERACIONES DE TAREAS (BACKEND)
# ==============================================================================

def add_task(title, user):
    """
    Crea una nueva tarea asociándola al usuario proporcionado.
    
    Mejora introducida: Validar que el título no esté vacío ni contenga solo espacios.
    """
    title_clean = title.strip()
    if not title_clean:
        raise ValueError("El título de la tarea no puede estar vacío.")

    tasks.append({
        "title": title_clean,
        "user": user,
        "completed": False
    })


def list_tasks(user):
    """
    Retorna únicamente las tareas pertenecientes al usuario especificado.
    
    Mejora introducida (Seguridad):
    Anteriormente devolvía la lista global `tasks` completa. Ahora filtra usando
    comprensión de listas para garantizar el aislamiento de datos por usuario.
    """
    return [task for task in tasks if task["user"] == user]


def _get_user_task_reference(index, user):
    """
    Función auxiliar para resolver la incoherencia de índices entre la vista filtrada y la lista global.
    
    DECISIÓN DEL DESARROLLADOR:
    Para evitar alterar la estructura simple de la lista global agregando UUIDs o IDs complejos,
    se obtiene la vista filtrada de las tareas del usuario (`user_tasks`) y se extrae la referencia
    directa al objeto diccionario en la posición relativa `index`. Esto garantiza que la modificación
    o eliminación opere sobre el objeto exacto en la lista global `tasks`.
    """
    if not isinstance(index, int):
        raise TypeError("El índice debe ser un número entero.")

    user_tasks = list_tasks(user)

    if index < 0 or index >= len(user_tasks):
        raise IndexError(f"El índice {index} no existe para las tareas de '{user}'.")

    # Retorna la referencia del diccionario original perteneciente al usuario
    return user_tasks[index]


def complete_task(index, user):
    """
    Marca como completada la tarea del usuario indicada por su índice relativo.
    
    Mejora introducida: Utiliza `_get_user_task_reference` para garantizar que solo se
    pueda modificar una tarea perteneciente al usuario autenticado.
    """
    target_task = _get_user_task_reference(index, user)
    target_task["completed"] = True
    return f"Tarea '{target_task['title']}' completada exitosamente."


def delete_task(index, user):
    """
    Elimina de la lista global la tarea del usuario indicada por su índice relativo.
    
    Mejora introducida: Obtiene la referencia real de la tarea del usuario y la remueve
    de la lista global `tasks`, evitando eliminar tareas ajenas.
    """
    target_task = _get_user_task_reference(index, user)
    tasks.remove(target_task)
    return f"Tarea '{target_task['title']}' eliminada exitosamente."


# ==============================================================================
# INTERFAZ GRÁFICA DE USUARIO (TKINTER GUI)
# ==============================================================================

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager - AI-Native Edition")
        self.root.geometry("920x620")
        self.root.minsize(820, 560)

        self.setup_style()
        self.create_variables()
        self.create_layout()
        self.refresh_tasks()

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def create_variables(self):
        self.current_user = tk.StringVar(value="ana")
        self.user_vars = {
            "ana": tk.BooleanVar(value=True),
            "jorge": tk.BooleanVar(value=False),
            "jojo": tk.BooleanVar(value=False)
        }
        self.task_title = tk.StringVar()
        self.task_index = tk.StringVar()
        self.status_text = tk.StringVar(value="Aplicación lista.")

    def create_layout(self):
        header = ttk.Frame(self.root, padding=(20, 15, 20, 5))
        header.pack(fill="x")

        ttk.Label(
            header,
            text="Task Manager",
            style="Title.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Aplicación segura de gestión de tareas por usuario",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(2, 0))

        top = ttk.Frame(self.root, padding=(20, 10))
        top.pack(fill="x")

        user_box = ttk.LabelFrame(top, text="Usuario actual", padding=12)
        user_box.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ttk.Label(
            user_box,
            text="Seleccione un usuario:"
        ).grid(row=0, column=0, sticky="w", padx=(0, 12))

        users_frame = ttk.Frame(user_box)
        users_frame.grid(row=0, column=1, sticky="w")

        for column, user in enumerate(("ana", "jorge", "jojo")):
            ttk.Checkbutton(
                users_frame,
                text=user.capitalize(),
                variable=self.user_vars[user],
                command=lambda selected_user=user: self.select_user(selected_user)
            ).grid(row=0, column=column, padx=(0, 14), sticky="w")

        task_box = ttk.LabelFrame(top, text="Nueva tarea", padding=12)
        task_box.pack(side="left", fill="x", expand=True, padx=(8, 0))

        ttk.Label(task_box, text="Título:").grid(
            row=0, column=0, sticky="w", padx=(0, 8)
        )

        ttk.Entry(
            task_box,
            textvariable=self.task_title,
            width=35
        ).grid(row=0, column=1, sticky="ew")

        ttk.Button(
            task_box,
            text="Crear tarea",
            style="Action.TButton",
            command=self.create_task
        ).grid(row=0, column=2, padx=(8, 0))

        task_box.columnconfigure(1, weight=1)

        table_frame = ttk.LabelFrame(
            self.root,
            text="Tareas registradas",
            padding=12
        )
        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(5, 10)
        )

        columns = ("index", "title", "user", "status")

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.tree.heading("index", text="#")
        self.tree.heading("title", text="Título")
        self.tree.heading("user", text="Usuario")
        self.tree.heading("status", text="Estado")

        self.tree.column("index", width=50, anchor="center")
        self.tree.column("title", width=430)
        self.tree.column("user", width=150, anchor="center")
        self.tree.column("status", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.on_task_selected
        )

        actions = ttk.LabelFrame(
            self.root,
            text="Acciones sobre tareas",
            padding=12
        )
        actions.pack(fill="x", padx=20, pady=(0, 10))

        ttk.Label(
            actions,
            text="Índice de tarea:"
        ).grid(row=0, column=0, padx=(0, 8))

        ttk.Entry(
            actions,
            textvariable=self.task_index,
            width=10
        ).grid(row=0, column=1, padx=(0, 12))

        ttk.Button(
            actions,
            text="Completar",
            style="Action.TButton",
            command=self.complete_selected
        ).grid(row=0, column=2, padx=5)

        ttk.Button(
            actions,
            text="Eliminar",
            style="Action.TButton",
            command=self.delete_selected
        ).grid(row=0, column=3, padx=5)

        ttk.Button(
            actions,
            text="Actualizar lista",
            command=self.refresh_tasks
        ).grid(row=0, column=4, padx=5)

        ttk.Button(
            actions,
            text="Limpiar índice",
            command=lambda: self.task_index.set("")
        ).grid(row=0, column=5, padx=5)

        ttk.Label(
            actions,
            text="Seleccione una tarea de la lista o escriba directamente su número (#).",
            wraplength=420
        ).grid(
            row=1,
            column=0,
            columnspan=6,
            sticky="w",
            pady=(10, 0)
        )

        status = ttk.Frame(
            self.root,
            padding=(20, 5, 20, 15)
        )
        status.pack(fill="x")

        ttk.Label(
            status,
            textvariable=self.status_text
        ).pack(side="left")

        ttk.Button(
            status,
            text="Salir",
            command=self.root.destroy
        ).pack(side="right")

    def select_user(self, selected_user):
        self.current_user.set(selected_user)

        for user, variable in self.user_vars.items():
            variable.set(user == selected_user)

        self.task_index.set("")
        self.refresh_tasks()

    def create_task(self):
        """
        Crea una nueva tarea e incluye manejo de errores de validación mediante GUI.
        """
        title = self.task_title.get()
        user = self.current_user.get()

        try:
            add_task(title, user)
            self.task_title.set("")
            self.refresh_tasks()
            self.status_text.set(f"Tarea creada para el usuario: {user}")
        except ValueError as err:
            messagebox.showwarning("Título inválido", str(err))

    def get_index(self):
        """
        Sanitiza y valida la entrada del campo de índice antes de convertirlo a entero.
        Evita un ValueError no controlado si el usuario ingresa texto o deja el campo vacío.
        """
        raw_val = self.task_index.get().strip()
        if not raw_val:
            raise ValueError("Por favor seleccione una tarea o introduzca un índice.")
        if not raw_val.isdigit():
            raise ValueError("El índice debe ser un número entero válido (0, 1, 2...).")
        return int(raw_val)

    def complete_selected(self):
        """
        Maneja la acción de completar una tarea seleccionada capturando excepciones específicas.
        """
        user = self.current_user.get()

        try:
            index = self.get_index()
            result = complete_task(index, user)
            self.task_index.set("")
            self.refresh_tasks()
            self.status_text.set(result)
        except (ValueError, IndexError, TypeError) as error:
            messagebox.showerror("Error en la operación", str(error))

    def delete_selected(self):
        """
        Maneja la acción de eliminar una tarea seleccionada capturando excepciones específicas.
        """
        user = self.current_user.get()

        try:
            index = self.get_index()
            result = delete_task(index, user)
            self.task_index.set("")
            self.refresh_tasks()
            self.status_text.set(result)
        except (ValueError, IndexError, TypeError) as error:
            messagebox.showerror("Error en la operación", str(error))

    def on_task_selected(self, event=None):
        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0], "values")

        if values:
            self.task_index.set(values[0])

    def refresh_tasks(self):
        """
        Refresca la tabla del Treeview mostrando ÚNICAMENTE las tareas del usuario actual.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        user = self.current_user.get()
        
        # Ahora list_tasks(user) devuelve únicamente las tareas pertenecientes al usuario actual.
        visible_tasks = list_tasks(user)

        for i, task in enumerate(visible_tasks):
            status = "Completada" if task["completed"] else "Pendiente"

            self.tree.insert(
                "",
                "end",
                values=(
                    i,  # Índice relativo al listado del usuario
                    task["title"],
                    task["user"],
                    status
                )
            )

        self.status_text.set(
            f"Usuario actual: {user} | Mis tareas: {len(visible_tasks)}"
        )


def main():
    root = tk.Tk()
    TaskManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
