from django.views.generic import ListView, DetailView
from .models import Shipment

class ShipmentListView(ListView):
    model = Shipment
    template_name = 'shipping/shipment_list.html'
    context_object_name = 'shipments'
    paginate_by = 20

class ShipmentDetailView(DetailView):
    model = Shipment
    template_name = 'shipping/shipment_detail.html'
    context_object_name = 'shipment'
