from odoo import _, models, fields, api


class Clinic(models.Model):
    _name = 'reclutamiento__kuale.clinic'
    _description = 'reclutamiento__kuale.clinic'

    active = fields.Boolean("Active", default=True)
    name = fields.Char('Name', required=True, translate=True)
    # zip_code = fields.Integer("Zip Code", required=True)
    street = fields.Char("Street", required=True)
    street2 = fields.Char("Street 2")
    zip = fields.Char("Zip", required=True)
    city = fields.Char("City", required=True)
    state_id = fields.Many2one(
        'res.country.state',
        string="State", domain="[('country_id', '=?', country_id)]", required=True)
    country_id = fields.Many2one('res.country', string="Country", required=True)
    address = fields.Char("Address", compute="_compute_address")
    description = fields.Text("Description")
    status = fields.Char("Status", compute="_compute_status")

    _sql_constraints = [
       ('name_uniq', 'unique (name)', "Age range name already exists!"),
    ]

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_("%s (copy)", self.name))
        return super(Clinic, self).copy(default)

    @api.depends('street', 'zip', 'city', 'state_id', 'country_id')
    def _compute_address(self):
        for address in self:
            address_parts = []

            # Concatenar los diferentes campos de la dirección
            street = address.street
            if street:
                address_parts.append(street)

            street2 = address.street2
            if street2:
                address_parts.append(street2)

            city = address.city
            if city:
                address_parts.append(city)

            state = address.state_id
            if state:
                address_parts.append(state.name)

            zip_address = address.zip
            if zip_address:
                address_parts.append(zip_address)

            country = address.country_id
            if country:
                address_parts.append(country.name)

            address.address = ', '.join(address_parts)

    @api.depends('active')
    def _compute_status(self):
        for record in self:
            if record.active:
                record.status = "Activo"
            else:
                record.status = "Inactivo"

