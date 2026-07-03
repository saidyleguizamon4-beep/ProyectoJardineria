from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from apps.clientes.models import Cliente, Propiedad
from apps.trabajos.models import Trabajo
from apps.facturacion.models import Factura

class FacturacionSeleccionarTrabajoTestCase(TestCase):
    def setUp(self):
        # Create client
        self.cliente = Cliente.objects.create(
            nombre="Juan",
            apellido="Perez",
            email="juan.perez@example.com",
            telefono="1234567",
            direccion="Calle 123"
        )
        # Create propiedad
        self.propiedad = Propiedad.objects.create(
            cliente=self.cliente,
            direccion="Calle 456",
            tipo="Casa",
            tiene_jardin=True
        )
        # Create jobs
        self.trabajo_sin_factura = Trabajo.objects.create(
            propiedad=self.propiedad,
            fecha_inicio=timezone.now(),
            estado="completado"
        )
        self.trabajo_con_factura = Trabajo.objects.create(
            propiedad=self.propiedad,
            fecha_inicio=timezone.now(),
            estado="completado"
        )
        # Create invoice for second job
        self.factura = Factura.objects.create(
            trabajo=self.trabajo_con_factura,
            numero_factura="FAC-00001",
            fecha_emision=timezone.now().date(),
            subtotal=100.0,
            iva=19.0,
            total=119.0,
            estado_pago="pendiente"
        )

    def test_seleccionar_trabajo_sin_sesion_redirects(self):
        response = self.client.get(reverse('facturacion:seleccionar_trabajo'))
        self.assertEqual(response.status_code, 302)

    def test_seleccionar_trabajo_con_sesion_lists_only_unvoiced_jobs(self):
        session = self.client.session
        session['logged_in'] = True
        session.save()

        response = self.client.get(reverse('facturacion:seleccionar_trabajo'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'facturacion/seleccionar_trabajo.html')
        
        # Check that only the job without an invoice is in context 'trabajos'
        trabajos_in_context = response.context['trabajos']
        self.assertEqual(len(trabajos_in_context), 1)
        self.assertEqual(trabajos_in_context[0].id_trabajo, self.trabajo_sin_factura.id_trabajo)

    def test_imprimir_factura_sin_sesion_redirects(self):
        response = self.client.get(reverse('facturacion:imprimir_factura', args=[self.factura.id_factura]))
        self.assertEqual(response.status_code, 302)

    def test_imprimir_factura_con_sesion_renders_correctly(self):
        session = self.client.session
        session['logged_in'] = True
        session.save()

        response = self.client.get(reverse('facturacion:imprimir_factura', args=[self.factura.id_factura]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'facturacion/imprimir_factura.html')
        self.assertContains(response, self.factura.numero_factura)
        self.assertContains(response, "119.00")


