from django.conf import settings
from django.apps import apps   
import json
import importlib



    # Pasos 
    # Empezar Migracion (enviandole que clave es: users, product) - OK
    # Construir un diccionario de los datos que se va a crear partiendo de las equivalencias
    # # Leer el JSON #OK
    # # Guardar el diccionario del JSON # OK
    # # Entrar a los niveles.
    # Guardar la informacion equivalente 



Equivalents = {
    'users' : {
        'before_model' : 'business.Company',
        'new_name_model' : 'core.User',
        'equivalents' : {
            'email' : {
                'type' : 'regular',
                'equivalent_field' : "email",
                'model_relation' : False
            },
            'first_name' : {
                'type' : 'regular',
                'equivalent_field' : "first_name",
                'model_relation' : False
            },
            'last_name' : {
                'type' : 'regular',
                'equivalent_field' : "last_name",
                'model_relation' : False

            }
        }
    }
}

class Migration :
    Model = None 
    JSON_Content = None
    JSON_Path = None
    TEMP_DictToSave = {}
    Equivalents = None
    Model_Project = None 

    def __init__(self, *args, **kwargs):

        # Read Equvilanets
        # Read Model that we want to migrate
        if "Equivalents" in kwargs:
            self.Equivalents = kwargs.get('Equivalents')
        if "Model" in kwargs:
            self.Model = kwargs.get('Model')
        if "Path" in kwargs: 
            self.JSON_Path = kwargs.get('Path')
        

    def __ReadJSON (self):
        with open(self.JSON_Path ,'r',encoding='utf-8') as archivo:
            self.JSON_Content = json.load(archivo)
            print("Nuestro equipo es el mejor !")
            return True

    def __ProcessFK (self):
        pass
    
    def __ProcessManyToMany(self):
        pass
    
    def __CleanDictToSave(self) :
        self.TEMP_DictToSave = {}


    def __EvaluateEquivalent(self, item):
        return item['type']

    def __Register (self, **kwargs):
        method = kwargs.get('method')
        before_field = kwargs.get('before_field')
        after_field = kwargs.get('after_field')
        item_json = kwargs.get('item_json')

        if method == 'regular' :
            self.TEMP_DictToSave[after_field['equivalent_field']] = item_json['fields'][before_field]
            '''
            MasterReference.objects.create(
                
            )
            '''
        if method == 'many_to_many':
            # Consultar Tabla Maestrea de Referencias
            # # old_pk, new_pk, before_model, after_model
            # #   1       25    mauth.Company business.Company

            # atencion registrar lower.
            new_pk_reference = []
            for item_number in item_json['fields'][before_field] : # [1,2,3,4,5] NOT "Hola mundo"
                Ref = MasterReference.objects.filter(old_pk=item_json['pk'], before_model=self.Equivalents[self.Model]['before_model'].lower())
                new_pk_reference.append(Ref[0].new_pk)

            self.TEMP_DictToSave[after_field['equivalent_field']] = new_pk_reference
            
        if method == 'fk': 
            Ref = MasterReference.objects.filter(old_pk=item_json['pk'], before_model=self.Equivalents[self.Model]['before_model'].lower())
            self.TEMP_DictToSave[after_field['equivalent_field']] = Ref[0].pk

    def SaveDatabase(self):
        try : 
            new_obj = self.Model_Project.objects.create(**self.TEMP_DictToSave)
            print (new_obj.pk)
        except: 
            print ("Ocurrio un error :: Migration :: SaveDatabase(self) ")

    def start (self, **kwargs):
        
        # Clean del DictToSave
        # Read JSON
        # Obtenemos el modelo a trabajar
        # # Recorremos el JSON de las migraciones
        # # # Registramos el viejo PK (ATENCION)
        # # # Recorremos los campos de los equivalentes registrados
        # # # # Evaluar y Registrar
        # # # # # Rellenamos el Diccionario  (Es la que cambia segun casos de NOFK, ManyToMany)
        # # # # Intentar registrar la informacion ya recolectada (Se debe mantner)

        # Clean del DictToSave

        self.__CleanDictToSave()
       
        # Read JSON
        self.__ReadJSON()

        # Obtenemos el modelo a trabajar
        self.Model_Project = apps.get_model(app_label=str(self.Equivalents[self.Model]['new_name_model'].split(".")[0]), model_name=str(self.Equivalents[self.Model]['new_name_model'].split(".")[1].lower()))

        # # Recorremos el JSON de las migraciones

        for item_json in self.JSON_Content :
            # # # Registramos el viejo PK (ATENCION)

            OLD_PK =  item_json['pk']

            # # # Recorremos los campos de los equivalentes registrados

            for key_item_equivalent, value_item_equivalent in self.Equivalents[self.Model]['equivalents'].items() :
                # # # # Evaluar y Registrar
                item = value_item_equivalent
                self.__Register(method=self.__EvaluateEquivalent(item), before_field=key_item_equivalent, after_field=item, item_json=item_json)

            self.SaveDatabase()




# Creating Object to Migrate Users Only
Obj_Users = Migration(
    Model='users',
    Equivalents=Equivalents,
    Path = settings.BASE_DIR + "/user.json"
    )
Obj_Users.start()

'''
