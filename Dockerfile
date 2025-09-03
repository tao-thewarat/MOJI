FROM odoo:18

USER root

# Install production dependencies
ADD requirements.txt /mnt/requirements.txt
RUN pip3 install --ignore-requires-python --break-system-packages -r /mnt/requirements.txt

USER odoo

# Setup Odoo
ADD --chown=odoo:odoo additional-addons /mnt/additional-addons
ADD --chown=odoo:odoo addons /mnt/addons
ADD --chown=odoo:odoo odoo.conf /etc/odoo/odoo.conf

USER root
RUN rm -rf /mnt/requirements.txt

USER odoo

EXPOSE 8069

CMD ["/usr/bin/odoo", "-c", "/etc/odoo/odoo.conf"]
