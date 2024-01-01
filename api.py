from flask import Flask, request, jsonify
import importlib
import os

app = Flask(__name__)

OPERATION_CLASSES = {}
PACKAGES_DIRECTORY = "tools"


def create_package_directory():
    if not os.path.exists(PACKAGES_DIRECTORY):
        os.makedirs(PACKAGES_DIRECTORY)


def save_python_code(package_name, python_code):
    package_path = os.path.join(PACKAGES_DIRECTORY, f"{package_name}_package.py")
    with open(package_path, "w", newline=os.linesep) as file:
        file.write(python_code)


def load_registered_packages():
    try:
        for file_name in os.listdir(PACKAGES_DIRECTORY):
            if file_name.endswith("_package.py"):
                package_name = file_name.replace("_package.py", "")
                module_name = f"{PACKAGES_DIRECTORY}.{package_name}_package"
                class_name = package_name.capitalize()

                try:
                    module = importlib.import_module(module_name)
                    module = importlib.reload(module)
                    class_ = getattr(module, class_name)
                    OPERATION_CLASSES[package_name] = class_
                except (ImportError, AttributeError) as e:
                    print(f"Failed to import module/class for operation '{package_name}': {e}")

    except Exception as e:
        print(f"Error loading registered packages: {e}")


create_package_directory()
load_registered_packages()


@app.route('/register_operation', methods=['POST'])
def register_operation_route():
    try:
        data = request.get_json()
        required_fields = ['package_name', 'python_code']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Save the provided Python code to the package location
        save_python_code(data['package_name'], data['python_code'])

        # Reload registered packages after a successful registration
        load_registered_packages()

        return jsonify({'message': f'Operation {data["package_name"]} registered successfully'})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/runsomething', methods=['POST'])
def runsomething():
    try:
        data = request.get_json()

        # Ensure required fields are present in the JSON
        required_fields = ['operation', 'input']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Get the class based on the operation from the registered classes
        operation_class = OPERATION_CLASSES.get(data['operation'])
        if operation_class is None:
            return jsonify({'error': f'Invalid operation: {data["operation"]}'}), 400

        # Instantiate the class with the provided input
        operation_instance = operation_class(*data['input'])

        # Call the relevant method (e.g., perform_multiplication or perform_division) based on the operation
        if hasattr(operation_instance, 'perform_multiplication'):
            result = operation_instance.perform_multiplication()
        elif hasattr(operation_instance, 'perform_division'):
            result = operation_instance.perform_division()
        else:
            return jsonify({'error': f'Method not found for operation: {data["operation"]}'}), 400

        return jsonify({'result': result})

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=False, host="localhost", port=5000)
