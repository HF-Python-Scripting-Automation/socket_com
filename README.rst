==========================================
Secure JSON Socket Server & Client Project
==========================================

.. image:: https://img.shields.io/badge/Python-3.12+-blue.svg
   :target: https://www.python.org/downloads/
.. image:: https://img.shields.io/badge/Ansible-2.15+-orange.svg
   :target: https://docs.ansible.com/

Ein hochverfügbares, verschlüsseltes Socket-System mit automatisiertem Deployment-Workflow.

Projektstruktur
===============

.. code-block:: text

    .
    ├── ansible.cfg          # SSH-Agent Forwarding & Defaults
    ├── deploy_server.yml    # Haupt-Playbook für das Deployment
    ├── inventory.ini        # Zielserver-IPs
    ├── pyproject.toml       # Projekt-Metadaten & Abhängigkeiten
    ├── secret.key           # Symmetrischer Fernet-Schlüssel
    ├── socket_com/          # Quellcode-Paket
    │   ├── client.py        # Verschlüsselter Client
    │   ├── server.py        # Verschlüsselter Multi-Client-Server
    │   └── scanner.py       # Port-Scanner für Server-Discovery
    └── templates/           # Systemd-Service-Unit-Vorlagen

------------------------------------------

Deployment mit Ansible
======================

Das Herzstück dieses Projekts ist das automatisierte Deployment. Mit einem einzigen Befehl werden alle Zielserver identisch konfiguriert.

Voraussetzungen
---------------

1. **SSH-Agent Forwarding**: 
   Da die Abhängigkeit ``psa_utils`` über ein privates Git-Repository bezogen wird, muss dein lokaler SSH-Key (der bei GitHub hinterlegt ist) im Agenten geladen sein. Ansible reicht diesen Key während der Installation an den Server weiter.

2. **Ansible**: 
   Muss auf dem Control-Node (z. B. Kali Linux) installiert sein.

Deployment-Schritte
-------------------

1. **SSH-Key lokal laden**:
   Stelle sicher, dass dein Key aktiv ist:

   .. code-block:: bash

      eval $(ssh-agent -s)
      ssh-add ~/.ssh/id_ed25519

2. **Server-IPs definieren**:
   Trage deine Ziel-IPs in die ``inventory.ini`` ein.

3. **Playbook starten**:
   Führe das Deployment aus. Ansible kümmert sich um Venv, Chown, Pip und Systemd-Reload:

   .. code-block:: bash

      ansible-playbook -i inventory.ini deploy_server.yml

------------------------------------------

Nutzung
=======

Client-Verbindung
-----------------

Nachdem der Server via Ansible auf ``0.0.0.0`` (alle Schnittstellen) gebunden wurde, kannst du den Client von deinem Kali-Host aus starten:

.. code-block:: bash

   python socket_com/client.py --host 192.168.110.10 --port 6543

Server-Discovery (Scanner)
--------------------------

Verwende den integrierten Scanner, um aktive Server-Instanzen in deinem Netzwerk zu finden:

.. code-block:: bash

   python socket_com/scanner.py

------------------------------------------

🛡 Sicherheitsmerkmale
======================

* **Verschlüsselung**: Nutzt das Fernet-Protokoll (AES-128 in CBC-Mode mit HMAC-SHA256).
* **Isolation**: Volle Trennung der Abhängigkeiten durch Python Virtual Environments.
* **Service-Management**: Automatischer Neustart bei Fehlern durch Systemd (``Restart=on-failure``).
* **Automatisierung**: Minimierung von Fehlkonfigurationen durch Infrastructure as Code (Ansible).

------------------------------------------

Troubleshooting
===============

* **Connection Refused**: 
  Überprüfe mit ``ss -tulpn | grep 6543`` auf dem Server, ob der Prozess auf ``0.0.0.0`` hört. Falls nicht, stelle sicher, dass ``daemon_reload: yes`` im Playbook ausgeführt wurde.
* **Git-Cloning Errors**: 
  Stelle sicher, dass ``ansible.cfg`` die Zeile ``ForwardAgent=yes`` enthält und dein SSH-Agent lokal läuft.