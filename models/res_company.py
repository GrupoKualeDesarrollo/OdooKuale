from odoo import fields, models, api


class res_company(models.Model):
    _inherit = 'res.company'

    #Razon social (Alfanumérico)
    business_name = fields.Char(string='Razon social', required=False, default="")
    #RFC (Alfanumérico)
    rfc = fields.Char(string='RFC', required=False, size=13,default="")
    #Representante legal (Selección)
    legal_representative = fields.Many2one(
        'reclutamiento__kuale.legal.representative',
        string='Representante legal',
        required=False
    )
    #Domicilio fiscal (Alfanumérico)
    fiscal_address = fields.Text(string='Domicilio fiscal', required=False)
    #Giro (Seleccion)
    business_type = fields.Many2one(
        'reclutamiento__kuale.business.type',
        string='Giro',
        required=False
    )
    #Registro patronal:IMSS (Seleccion)
    imss_registration = fields.Many2one(
        'reclutamiento__kuale.imss.registration',
        string='Registro patronal (IMSS)',
        required=False
    )
    #Certificado para timbrado (Seleccion)
    certificate_for_stamp = fields.Many2one(
        'reclutamiento__kuale.digital.stamp.certificate',
        string='Certificado para timbrado',
        required=False
    )
    #Fecha de apertura (Fecha)
    opening_date = fields.Date(string='Fecha de apertura', required=False)
    # SUCURSALES
    #No. de tienda
    no_store = fields.Integer(string='No.de tienda', required=True, default=None)
    # Tipo de Sucursal (Selección unica)
    branch_type = fields.Many2one('reclutamiento__kuale.branch.type', string='Tipo de Sucursal', required=False)
    # Nombre sucursal
    branch_name = fields.Char(string='Nombre sucursal', required=True)
    # Reporta a (seleccion)
    reports_to = fields.Many2one('res.users', string='Reporta a',
                                 domain="[('company_id', '=', parent_id), ('active', '=', True)]")
    # Entrenador (Selección múltiple)
    trainers = fields.Many2many('res.users', string='Entrenador(es)',
                                domain="[('company_id', '=', parent_id), ('active', '=', True)]")
    #Guia general
    general_guide = fields.Many2one('res.users', string='Guía General',
                                domain="[('company_id', '=', parent_id), ('active', '=', True)]")
    # Capacitación (Selección múltiple)
    training_available = fields.Boolean(string='Capacitación')
    # Metros cuadrados de construcción (Numérico)
    construction_area = fields.Float(string='Metros cuadrados de construcción')
    # Metros cuadrados de terreno (Numérico)
    land_area = fields.Float(string='Metros cuadrados de terreno')
    # Layout (File)
    layout = fields.Binary(string='Layout')
    layout_filename = fields.Char(string='Layout (Croquis)')
    # Póliza de seguro
    insurance_policy = fields.Binary(string='Póliza de seguro')
    insurance_policy_filename = fields.Char(string='Póliza de seguro')
    #Entre calles
    between_streets = fields.Text(string='Entre calles')
    #Diferencia sucursal de company
    is_parent_id_set = fields.Boolean(compute='_compute_is_parent_id_set', store=True)
    @api.onchange('rfc')
    def set_caps(self):
      rfc_aux = str(self.rfc)
      self.rfc = rfc_aux.upper()

    @api.depends('parent_id')
    def _compute_is_parent_id_set(self):
        for record in self:
            record.is_parent_id_set = bool(record.parent_id)
        print(f"is_parent_id_set value for record {record.id}: {record.is_parent_id_set}")
