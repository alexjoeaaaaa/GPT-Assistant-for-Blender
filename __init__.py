bl_info = {
    "name": "GPT Assistant",
    "author": "joehsuang",
    "version": (1, 0),
    "blender": (4, 3, 2),
    "location": "View3D > Tools",
    "description": "Execute GPT-generated Python code in Blender",
    "category": "3D View"
}

import bpy
import os
import threading
import traceback
import tempfile


# === 文件操作：保存和加载 API Key ===
def get_api_key_file():
    config_path = os.path.join(
        bpy.utils.resource_path('USER'),
        "scripts",
        "addons",
        "gptaddons"
    )
    os.makedirs(config_path, exist_ok=True)
    return os.path.join(config_path, "api_key.txt")


def save_api_key_to_file(api_key):
    key_file = get_api_key_file()
    with open(key_file, "w", encoding="utf-8") as f:
        f.write(api_key.strip())


def load_api_key_from_file():
    key_file = get_api_key_file()
    if os.path.exists(key_file):
        with open(key_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


# === 同步请求 GPT ===
def sync_fetch_gpt_response(prompt, api_key):
    import openai
    openai.api_key = api_key

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {e}"


# === 提取代码 ===
def extract_code(response):
    try:
        start = response.find("```python") + len("```python")
        end = response.find("```", start)
        if start == -1 or end == -1:
            print("No valid Python code block found in GPT response:")
            print(response)
            raise ValueError("No valid Python code block found.")
        code = response[start:end].strip()
        return code.replace("：", ":").replace("（", "(").replace("）", ")")
    except Exception as e:
        print(f"Error extracting code from response: {e}")
        print("Full GPT response:")
        print(response)
        raise


# === 保存到文件并通过 bpy 执行 ===
def save_to_file_and_execute(code, filename="gpt_generated_code.py"):
    try:
        # 临时文件路径
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)

        # 将代码保存到文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

        # 使用 Blender 的 API 执行脚本文件
        bpy.ops.script.python_file_run(filepath=filepath)

        print(f"Code saved to '{filepath}' and executed successfully.")
    except Exception as e:
        print(f"Error executing code from file: {e}")
        traceback.print_exc()


# === 后台执行任务 ===
def fetch_and_execute_in_background(prompt, api_key):
    """
    在后台线程中请求 GPT，并将代码保存到文件并执行
    """
    def background_task():
        print("Fetching GPT response in background...")
        # 拼接用户提示
        full_prompt = (
            "你是一名专门生成 Blender Python 脚本的助手。\n"
            "如果输入是指令，请返回以下格式的内容：\n"
            "Python代码：<Blender 可运行的 Python 脚本，仅包含代码，无解释>\n"
            "请确保生成的脚本兼容 Blender 4.3.2，所有材质和节点指令必须完全支持。\n"
            "请确保生成的脚本內無全形字體，一定要盡力避免多餘的標點符號，因為這些代碼是由別的代碼呼叫，有可能會因為各式的標點符號造成程式被打斷"
            f"任务是：{prompt}"
        )

        response = sync_fetch_gpt_response(full_prompt, api_key)
        print("Full GPT Response:")
        print(response)

        if "Python代码：" in response:
            try:
                code = extract_code(response)
                bpy.app.timers.register(lambda: save_to_file_and_execute_in_main_thread(code))
            except ValueError as e:
                print(f"Error: {e}")
        else:
            print("GPT did not return valid code. Response was:")
            print(response)

    thread = threading.Thread(target=background_task)
    thread.start()


def save_to_file_and_execute_in_main_thread(code):
    save_to_file_and_execute(code)
    return None


# === 插件偏好设置 ===
class GPTAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "gptaddons"

    def draw(self, context):
        layout = self.layout
        layout.label(text="GPT Assistant Settings")
        layout.operator("gptaddons.edit_api_key", text="Set API Key")
        layout.operator("gptaddons.show_api_key", text="Show API Key")


# === 操作类：编辑 API Key ===
class GPT_OT_EditAPIKey(bpy.types.Operator):
    bl_idname = "gptaddons.edit_api_key"
    bl_label = "Edit API Key"

    api_key: bpy.props.StringProperty(name="API Key", default="", subtype='NONE')

    def invoke(self, context, event):
        self.api_key = load_api_key_from_file()
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        save_api_key_to_file(self.api_key)
        self.report({'INFO'}, "API Key saved successfully.")
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "api_key", text="Enter API Key")


# === 操作类：执行 GPT 指令 ===
class GPT_OT_ExecuteCommand(bpy.types.Operator):
    bl_idname = "gptaddons.execute_command"
    bl_label = "Execute GPT Command"

    def execute(self, context):
        api_key = load_api_key_from_file()
        if not api_key:
            self.report({'ERROR'}, "API Key not found. Please set it in the preferences.")
            return {'CANCELLED'}

        # 获取 Prompt 输入框的内容
        user_prompt = context.scene.gpt_prompt

        # 在后台请求和执行
        fetch_and_execute_in_background(user_prompt, api_key)
        self.report({'INFO'}, "Fetching GPT response in background...")
        return {'FINISHED'}


# === 面板 ===
class GPT_PT_Panel(bpy.types.Panel):
    bl_label = "GPT Assistant"
    bl_idname = "GPT_PT_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "GPT"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "gpt_prompt", text="Prompt")
        layout.operator("gptaddons.execute_command", text="Run GPT Command")


# === 注册和卸载 ===
def register():
    bpy.utils.register_class(GPTAddonPreferences)
    bpy.utils.register_class(GPT_OT_EditAPIKey)
    bpy.utils.register_class(GPT_OT_ExecuteCommand)
    bpy.utils.register_class(GPT_PT_Panel)
    bpy.types.Scene.gpt_prompt = bpy.props.StringProperty(
        name="GPT Prompt",
        description="Enter a command for GPT to process",
        default=""
    )


def unregister():
    bpy.utils.unregister_class(GPTAddonPreferences)
    bpy.utils.unregister_class(GPT_OT_EditAPIKey)
    bpy.utils.unregister_class(GPT_OT_ExecuteCommand)
    bpy.utils.unregister_class(GPT_PT_Panel)
    del bpy.types.Scene.gpt_prompt


if __name__ == "__main__":
    register()
