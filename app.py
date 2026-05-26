from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import json
import csv
import io
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
CORS(app)

# Configuration
MONTANT_COTISATION = 11000  # 10000 + 1000 restauration
DELAI_JOURS = 60  # 2 mois

# Initialisation base de données
def init_db():
    conn = sqlite3.connect('/data/data/com.termux/files/home/vomasi/vomasi.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS membres
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nom TEXT NOT NULL,
                  prenom TEXT NOT NULL,
                  localite TEXT,
                  telephone TEXT,
                  derniere_cotisation DATE,
                  beneficiaire TEXT DEFAULT 'Aucun')''')
    c.execute('''CREATE TABLE IF NOT EXISTS cotisations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  membre_id INTEGER,
                  montant INTEGER,
                  date_paiement DATE,
                  beneficiaire_nom TEXT,
                  FOREIGN KEY (membre_id) REFERENCES membres (id))''')
    conn.commit()
    conn.close()

# Vérifier si un membre est à jour
def is_up_to_date(membre_id):
    conn = sqlite3.connect('/data/data/com.termux/files/home/vomasi/vomasi.db')
    c = conn.cursor()
    c.execute("SELECT derniere_cotisation FROM membres WHERE id = ?", (membre_id,))
    result = c.fetchone()
    conn.close()
    if not result or not result[0]:
        return False
    last_date = datetime.strptime(result[0], '%Y-%m-%d')
    return (datetime.now() - last_date).days <= DELAI_JOURS

# Vérifier les retards et notifier
def check_late_members():
    while True:
        conn = sqlite3.connect('/data/data/com.termux/files/home/vomasi/vomasi.db')
        c = conn.cursor()
        c.execute("SELECT id, nom, prenom FROM membres")
        membres = c.fetchall()
        conn.close()
        for m in membres:
            if not is_up_to_date(m[0]):
                print(f"🔔 ALERTE: {m[1]} {m[2]} est en retard de cotisation!")
        time.sleep(3600)  # Vérifie toutes les heures

# Démarrer le thread de notification
threading.Thread(target=check_late_members, daemon=True).start()

# Page d'accueil - Interface principale
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VOMASI - Gestion des cotisations</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .login-form, .main-menu {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .input-group {
            margin-bottom: 15px;
        }
        input, select, button {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background: #764ba2;
        }
        .btn-danger {
            background: #e74c3c;
        }
        .btn-success {
            background: #27ae60;
        }
        .member-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }
        .member-card.retard {
            border-left-color: #e74c3c;
            background: #fee;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .search-box {
            margin-bottom: 20px;
        }
        .stats {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            margin-top: 10px;
        }
        .stats.up {
            background: #27ae60;
            color: white;
        }
        .stats.late {
            background: #e74c3c;
            color: white;
        }
        .nav-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .nav-buttons button {
            flex: 1;
            min-width: 120px;
        }
        @media (max-width: 768px) {
            .nav-buttons button {
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 Association VOMASI</h1>
            <p>Système de gestion des cotisations</p>
        </div>
        
        <div id="content">
            <!-- Contenu chargé dynamiquement -->
        </div>
    </div>

    <script>
        let loggedIn = false;
        
        function showLogin() {
            document.getElementById('content').innerHTML = `
                <div class="login-form">
                    <h2>🔐 Accès restreint</h2>
                    <div class="input-group">
                        <input type="text" id="username" placeholder="Identifiant">
                    </div>
                    <div class="input-group">
                        <input type="password" id="password" placeholder="Mot de passe">
                    </div>
                    <button onclick="login()">Se connecter</button>
                </div>
            `;
        }
        
        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            });
            
            const data = await response.json();
            if (data.success) {
                loggedIn = true;
                showMainMenu();
            } else {
                alert('Accès refusé');
            }
        }
        
        function showMainMenu() {
            document.getElementById('content').innerHTML = `
                <div class="main-menu">
                    <div class="nav-buttons">
                        <button onclick="showMembers()">📋 Tous les membres</button>
                        <button onclick="showAddMember()">➕ Nouveau membre</button>
                        <button onclick="showPay()">💰 Enregistrer cotisation</button>
                        <button onclick="showSearch()">🔍 Rechercher</button>
                        <button onclick="showBeneficiary()">👑 Choisir bénéficiaire</button>
                        <button onclick="exportCSV()">📁 Export CSV</button>
                        <button onclick="showLateMembers()">⚠️ Membres en retard</button>
                    </div>
                    <div id="subcontent">
                        <h3>Bienvenue dans VOMASI</h3>
                        <p>Montant cotisation: ${MONTANT_COTISATION} FCFA (10000 + 1000 restauration)</p>
                        <p>Périodicité: tous les 2 mois (60 jours)</p>
                    </div>
                </div>
            `;
        }
        
        async function showMembers() {
            const response = await fetch('/api/membres');
            const membres = await response.json();
            
            let html = '<h3>📋 Liste des membres</h3><div class="grid">';
            for (const m of membres) {
                const status = m.a_jour ? 'À jour' : '⚠️ Retard';
                const statusClass = m.a_jour ? 'up' : 'late';
                html += `
                    <div class="member-card ${!m.a_jour ? 'retard' : ''}">
                        <strong>${m.nom} ${m.prenom}</strong><br>
                        📍 ${m.localite || 'Non renseigné'}<br>
                        📞 ${m.telephone || 'Non renseigné'}<br>
                        💵 ${status}<br>
                        📅 Dernière cotisation: ${m.derniere_cotisation || 'Jamais'}<br>
                        <span class="stats ${statusClass}">${status}</span>
                    </div>
                `;
            }
            html += '</div><button onclick="showMainMenu()" style="margin-top:20px">Retour</button>';
            document.getElementById('subcontent').innerHTML = html;
        }
        
        function showAddMember() {
            document.getElementById('subcontent').innerHTML = `
                <h3>➕ Ajouter un membre</h3>
                <div class="input-group"><input type="text" id="nom" placeholder="Nom"></div>
                <div class="input-group"><input type="text" id="prenom" placeholder="Prénom"></div>
                <div class="input-group"><input type="text" id="localite" placeholder="Localité"></div>
                <div class="input-group"><input type="tel" id="telephone" placeholder="Téléphone"></div>
                <button onclick="addMember()">Enregistrer</button>
                <button onclick="showMainMenu()">Annuler</button>
            `;
        }
        
        async function addMember() {
            const data = {
                nom: document.getElementById('nom').value,
                prenom: document.getElementById('prenom').value,
                localite: document.getElementById('localite').value,
                telephone: document.getElementById('telephone').value
            };
            
            const response = await fetch('/api/membres', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            alert(result.message);
            showMainMenu();
        }
        
        function showPay() {
            document.getElementById('subcontent').innerHTML = `
                <h3>💰 Enregistrer un paiement</h3>
                <div class="input-group"><input type="text" id="searchNom" placeholder="Nom du membre"></div>
                <button onclick="searchMemberForPay()">Chercher</button>
                <div id="payResult"></div>
                <button onclick="showMainMenu()">Retour</button>
            `;
        }
        
        async function searchMemberForPay() {
            const nom = document.getElementById('searchNom').value;
            const response = await fetch(`/api/recherche?nom=${encodeURIComponent(nom)}`);
            const membres = await response.json();
            
            if (membres.length === 0) {
                alert('Membre non trouvé');
                return;
            }
            
            let html = '<h4>Résultats:</h4>';
            for (const m of membres) {
                html += `
                    <div class="member-card">
                        ${m.nom} ${m.prenom} - ${m.localite}
                        <button onclick="payMember(${m.id})" class="btn-success">Enregistrer paiement (${MONTANT_COTISATION} FCFA)</button>
                    </div>
                `;
            }
            document.getElementById('payResult').innerHTML = html;
        }
        
        async function payMember(id) {
            const response = await fetch('/api/cotisation', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({membre_id: id})
            });
            const result = await response.json();
            alert(result.message);
            showMainMenu();
        }
        
        async function showSearch() {
            document.getElementById('subcontent').innerHTML = `
                <h3>🔍 Rechercher un membre</h3>
                <div class="input-group"><input type="text" id="searchTerm" placeholder="Nom ou prénom"></div>
                <button onclick="searchMember()">Rechercher</button>
                <div id="searchResult"></div>
                <button onclick="showMainMenu()">Retour</button>
            `;
        }
        
        async function searchMember() {
            const term = document.getElementById('searchTerm').value;
            const response = await fetch(`/api/recherche?nom=${encodeURIComponent(term)}`);
            const membres = await response.json();
            
            if (membres.length === 0) {
                document.getElementById('searchResult').innerHTML = '<p>Aucun résultat</p>';
                return;
            }
            
            let html = '<h4>Résultats:</h4>';
            for (const m of membres) {
                const status = m.a_jour ? '✅ À jour' : '⚠️ Retard';
                html += `
                    <div class="member-card ${!m.a_jour ? 'retard' : ''}">
                        <strong>${m.nom} ${m.prenom}</strong><br>
                        📍 ${m.localite}<br>
                        📞 ${m.telephone}<br>
                        💵 ${status}<br>
                        📅 Dernière cotisation: ${m.derniere_cotisation || 'Jamais'}
                    </div>
                `;
            }
            document.getElementById('searchResult').innerHTML = html;
        }
        
        function showBeneficiary() {
            document.getElementById('subcontent').innerHTML = `
                <h3>👑 Désigner le bénéficiaire</h3>
                <div class="input-group"><input type="text" id="benefNom" placeholder="Nom du membre bénéficiaire"></div>
                <button onclick="setBeneficiary()">Valider</button>
                <button onclick="showMainMenu()">Retour</button>
            `;
        }
        
        async function setBeneficiary() {
            const nom = document.getElementById('benefNom').value;
            const response = await fetch('/api/beneficiaire', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({nom})
            });
            const result = await response.json();
            alert(result.message);
            showMainMenu();
        }
        
        async function showLateMembers() {
            const response = await fetch('/api/retards');
            const membres = await response.json();
            
            let html = '<h3>⚠️ Membres en retard de cotisation</h3><div class="grid">';
            for (const m of membres) {
                html += `
                    <div class="member-card retard">
                        <strong>${m.nom} ${m.prenom}</strong><br>
                        📍 ${m.localite}<br>
                        📞 ${m.telephone}<br>
                        📅 Dernière cotisation: ${m.derniere_cotisation || 'Jamais'}
                    </div>
                `;
            }
            html += '</div><button onclick="showMainMenu()">Retour</button>';
            document.getElementById('subcontent').innerHTML = html;
        }
        
        async function exportCSV() {
            window.open('/api/export', '_blank');
            alert('Export en cours...');
        }
        
        // Démarrage
        showLogin();
        
        const MONTANT_COTISATION = ${MONTANT_COTISATION};
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if data.get('username') == 'presidente' and data.get('password') == 'vomasi2025':
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/membres')
def get_membres():
    conn = sqlite3.connect('/data/data/com.termux/files/home/vomasi/vomasi.db')
    c = conn.cursor()
    c.execute("SELECT id, nom, prenom, localite, telephone, derniere_cotisation FROM membres")
    membres = []
    for row in c.fetchall():
        membres.append({
            'id': row[0],
            'nom': row[1],
            'prenom': row[2],
            'localite': row[3],
            'telephone': row[4],
            'derniere_cotisation': row[5],
            'a_jour': is_up_to_date(row[0])
        })
    conn.close()
    return jsonify(membres)

@app.route('/api/membres', methods=['POST'])
def add_membre():
    data = request.json
    conn = sqlite3.connect('/data/data/com.termux/files/home/vomasi/vomasi.db')
    c = conn.cursor()
    c.execute("INSERT INTO membres (nom, prenom, localite, telephone, derniere_cotisation) VALUES (?,?,?,?,?)",
              (data['nom'], data['prenom'], data['localite'], data['telephone'], None))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Membre ajouté avec succès'})

@app.route('/api/cotisation', methods=['POST'])
def add_cotisation():
    data = request.json
    membre_id = data['membre_id']
    date_paiement = datetime.now().strftime('%Y-%m-%d')
    
    # Récupérer le bénéficiaire actuel
    conn = sqlite3.connect('/data/data/com.termux/files/home/vomasi/vomasi.db')
    c = conn.cursor()
    c.execute("SELECT beneficiaire FROM membres WHERE beneficiaire != 'Aucun' LIMIT 1")
    benef = c.fetchone()
    beneficiaire_nom = benef[0] if benef else 'Non désigné'
    
    # Enregistrer cotisation
    c.execute("INSERT INTO cotisations (membre_id, montant, date_paiement, beneficiaire_nom) VALUES (?,?,?,?)",
              (membre_id, MONTANT_COTISATION, date_paiement, beneficiaire_nom))
    
    # Mettre à jour la date du membre
    c.execute("UPDATE membres SET derniere_cotisation = ? WHERE id = ?", (date_paiement, membre_id))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Paiement de {MONTANT_COTISATION} FCFA enregistré'})

@app.route('/api/recherche')
def recherche():
    nom = request.args.get('nom', '')
    conn = sqlite3.connect('/data/data/com.termux/files/home/vomasi/vomasi.db')
    c = conn.cursor()
    c.execute("SELECT id, nom, prenom, localite, telephone, derniere_cotisation FROM membres WHERE nom LIKE ? OR prenom LIKE ?",
              (f'%{nom}%', f'%{nom}%'))
    membres = []
    for row in c.fetchall():
        membres.append({
            'id': row[0],
            'nom': row[1],
            'prenom': row[2],
            'localite': row[3],
            'telephone': row[4],
            'derniere_cotisation': row[5],
            'a_jour': is_up_to_date(row[0])
        })
    conn.close()
    return jsonify(membres)

@app.route('/api/retards')
def get_retards():
    conn = sqlite3.connect('/data/data/com.termux/files/home/vomasi/vomasi.db')
    c = conn.cursor()
    c.execute("SELECT id, nom, prenom, localite, telephone, derniere_cotisation FROM membres")
    membres = []
    for row in c.fetchall():
        if not is_up_to_date(row[0]):
            membres.append({
                'id': row[0],
                'nom': row[1],
                'prenom': row[2],
                'localite': row[3],
                'telephone': row[4],
                'derniere_cotisation': row[5] or 'Jamais'
            })
    conn.close()
    return jsonify(membres)

@app.route('/api/beneficiaire', methods=['POST'])
def set_beneficiaire():
    data = request.json
    nom = data.get('nom')
    conn = sqlite3.connect('/data/data/com.termux/files/home/vomasi/vomasi.db')
    c = conn.cursor()
    # Réinitialiser tous les bénéficiaires
    c.execute("UPDATE membres SET beneficiaire = 'Aucun'")
    # Définir le nouveau bénéficiaire
    c.execute("UPDATE membres SET beneficiaire = ? WHERE nom = ?", (nom, nom))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Bénéficiaire désigné: {nom}'})

@app.route('/api/export')
def export_csv():
    conn = sqlite3.connect('/data/data/com.termux/files/home/vomasi/vomasi.db')
    c = conn.cursor()
    c.execute("SELECT nom, prenom, localite, telephone, derniere_cotisation, beneficiaire FROM membres")
    rows = c.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Nom', 'Prénom', 'Localité', 'Téléphone', 'Dernière cotisation', 'Statut', 'Bénéficiaire'])
    
    for row in rows:
        status = 'À jour' if row[4] and (datetime.now() - datetime.strptime(row[4], '%Y-%m-%d')).days <= DELAI_JOURS else 'Retard'
        writer.writerow([row[0], row[1], row[2], row[3], row[4] or 'Jamais', status, row[5]])
    
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8-sig')),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='vomasi_membres.csv')

if __name__ == '__main__':
    init_db()
    print("=" * 50)
    print("🏠 Serveur VOMASI démarré!")
    print("📱 Ouvre ton navigateur sur: http://localhost:5000")
    print("🔐 Identifiant: presidente | Mot de passe: vomasi2025")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)

