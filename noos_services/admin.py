from django.contrib import admin

# Register your models here.
from .models import Forcing, ForcingCouple, LoggingMessage, Node, NoosModel, SimulationCloud, SimulationDemand, \
    SimulationElement, SimulationMetadata, UploadedFile

admin.site.register(Node)
admin.site.register(SimulationDemand)
admin.site.register(Forcing)
admin.site.register(NoosModel)
admin.site.register(LoggingMessage)
admin.site.register(ForcingCouple)
admin.site.register(UploadedFile)
admin.site.register(SimulationElement)
admin.site.register(SimulationCloud)
admin.site.register(SimulationMetadata)
