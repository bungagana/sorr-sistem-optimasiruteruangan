#--------------------- LIBRARY ---------------------------------
import streamlit as st
import random
from streamlit_option_menu import option_menu
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from graphviz import Digraph
import numpy as np

# ------------- Inisialisasi variabel dan parameter --------------
alpha = 1
beta = 1
pho = 0.5
tau = 0.01
NCmax = 2
Q = 1
jumlah_semua_semut = 5
jumlah_ruangan = 5
feromon = [[tau] * jumlah_ruangan for _ in range(jumlah_semua_semut)]
jarak = [
    [0, 5, 7, 3, None],     # A: [A, B, C, D, E]
    [5, 0, 4, None, 3],     # B: [A, B, C, D, E]
    [7, 4, 0, None, 5],     # C: [A, B, C, D, E]
    [3, None, None, 0, 4],  # D: [A, B, C, D, E]
    [None, None, 5, 4, 0]   # E: [A, B, C, D, E]
]
# Fungsi untuk memilih ruangan selanjutnya berdasarkan probabilitas
def pilih_ruangan(semut, ruangan_sekarang, ruangan_tersedia):
    probabilitas = []
    total = 0
    for ruangan in ruangan_tersedia:
        nilai_feromon = feromon[semut][ruangan]
        jarak_ruangan = jarak[ruangan_sekarang][ruangan]
        if jarak_ruangan is None:
            continue
        heuristik = 1 / jarak_ruangan
        probabilitas.append((ruangan, nilai_feromon * alpha * heuristik * beta))
        total += nilai_feromon * alpha * heuristik * beta

    probabilitas = [(ruangan, prob / total) for ruangan, prob in probabilitas]
    probabilitas.sort(key=lambda x: x[1], reverse=True)
    probabilitas = [(ruangan, prob / total) for ruangan, prob in probabilitas]  # Normalisasi probabilitas
    return probabilitas[0][0]

#### ----- NAVIGATION BAR ---- ####
selected = option_menu(
    menu_title="SOR(Sistem Optimasi Rute Ruangan)",
    options=["Home",  "Show", "Input"],
    icons=["house", "columns","input-cursor"],
    menu_icon="caret-right-square-fill",
    orientation="horizontal",  # Mengubah orientasi menu menjadi vertikal
    styles={
        "container": {"padding": "0!important", "background-color": "black"},
        "icon": {"color": "white", "font-size": "10px"},
        "nav-link": {
            "font-size": "15px",
            "font-colour": "white",
            "text-align": "center",
            "margin": "0px",
            "--hover-color": "#eeeee",
        },
        "nav-link-selected": {"background-color": "#696666"},
    },
)

#### ----- SECTION HOME ---- ####
if selected == "Home":
    #--------- DESCRIPTION  -------------------
    st.header("Kasus")
    st.markdown(
        "<div style='text-align: justify;'>Terdapat pasien yang menderita penyakit jantung dan perlu ditangani secara cepat dan berkala. Di dalam rumah sakit yang menangani penyakit dalam, terdapat 5 ruangan yang diibaratkan menjadi ruangan A (ruang tunggu pasien), B (ruang pendaftaran), C (ruang pengecekan dasar), D (ruang dokter) dan E (laboratorium). Agar pasien dapat ditangani dengan lebih cepat dapat diperkirakan menggunakan perhitungan algoritma koloni semut sebagai berikut ini. Diketahui:</div>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    
    #-------------  BUAT GRAF  -------------------
    # Membuat graf kosong
    G = nx.Graph()
    # Menambahkan node ke graf
    nodes = ['A', 'B', 'C', 'D', 'E']
    G.add_nodes_from(nodes)
    # Menambahkan edge dan bobotnya ke graf
    edges = [
        ('A', 'B', 5),
        ('A', 'C', 7),
        ('A', 'D', 3),
        ('B', 'C', 4),
        ('C', 'E', 5),
        ('D', 'E', 4)
    ]
    G.add_weighted_edges_from(edges)

    # Mengambil posisi node untuk tata letak graf
    pos = nx.spring_layout(G)
    # Mengambil bobot edge untuk label
    edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
    
    # Menggambar node dan edge
    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    # Menampilkan graf
    plt.axis('off')
    plt.savefig("graph.png")
    st.image("graph.png")
    st.markdown("---")

    # Fungsi untuk update feromon setiap siklus
    def update_feromon():
        for i in range(jumlah_semua_semut):
            for j in range(jumlah_ruangan):
                feromon[i][j] *= pho

    # Algoritma koloni semut
    def optimisasi_koloni_semut():
        solusi_terbaik = []
        jarak_terbaik = float('inf')

        for siklus in range(NCmax):
            solusi = [[] for _ in range(jumlah_semua_semut)]
            jarak_semut = [0] * jumlah_semua_semut

            for semut in range(jumlah_semua_semut):
                ruangan_sekarang = 0  # Ruang awal
                ruangan_tersedia = list(range(1, jumlah_ruangan))
                solusi_semut = [0]  # Menambahkan ruang awal A ke solusi

                while ruangan_tersedia:
                    ruangan_selanjutnya = pilih_ruangan(semut, ruangan_sekarang, ruangan_tersedia)
                    solusi_semut.append(ruangan_selanjutnya)
                    jarak_semut[semut] += jarak[ruangan_sekarang][ruangan_selanjutnya]

                    ruangan_tersedia.remove(ruangan_selanjutnya)
                    ruangan_sekarang = ruangan_selanjutnya

                jarak_semut[semut] += jarak[ruangan_sekarang][0]  # Kembali ke ruang A
                solusi_semut.append(0)  # Menambahkan ruang A ke solusi

                # Update solusi terbaik
                if jarak_semut[semut] < jarak_terbaik:
                    jarak_terbaik = jarak_semut[semut]
                    solusi_terbaik = solusi_semut

            update_feromon()
        return solusi_terbaik, jarak_terbaik
    
     #-------------  TAMPIL RUTE  -------------------
    # Menjalankan algoritma koloni semut
    solusi_terbaik, jarak_terbaik = optimisasi_koloni_semut()
    st.header("Rute terbaik:")
    st.write([chr(ruangan + ord('A')) for ruangan in solusi_terbaik])
    st.markdown("---")
    
     #-------------  TAMPIL JARAK  -------------------
    st.header("Jarak terbaik:")
    st.write(jarak_terbaik)
    st.markdown("---")

     #-------------  BUAT VISUAL RUTE  -------------------
    # Membuat diagram grafik menggunakan Graphviz
    graph = Digraph()

    for i in range(jumlah_ruangan):
        graph.node(str(i), label=f"Ruangan {chr(i+ord('A'))}")

    for i in range(len(solusi_terbaik) - 1):
        ruangan_saat_ini = solusi_terbaik[i]
        ruangan_selanjutnya = solusi_terbaik[i+1]
        graph.edge(str(ruangan_saat_ini), str(ruangan_selanjutnya))

    # Menampilkan diagram grafik menggunakan st.graphviz_chart
    st.header("Visualisasi Rute:")
    st.graphviz_chart(graph.source)
    st.markdown("Jadi berdasar kasus diatas, pasien yang berasal dari ruang A akan mendapatkan penanganan ke ruangan B dengan cepat dengan cara melewati ruangan D kemudian E, ruangan C baru kemudian sampai ke ruangan B") 
    st.markdown("---")
    st.caption("Developed by bunga")


#### ----- SECTION SHOW ---- ####
elif selected == "Show":
    st.header("Show")
    st.write("Klik tombol 'Next' untuk melihat rute terbaik untuk setiap semut.")

    #-------------  BUAT TAMPILAN PER TAHAP  -------------------
    # Buat tombol untuk setiap semut
    ant_buttons = []
    for i in range(jumlah_semua_semut):
        ant_buttons.append(st.button(f"Lanjut Pasien {i+1}"))

    # Variabel untuk melacak rute saat ini untuk setiap semut
    current_routes = [[] for _ in range(jumlah_semua_semut)]
    current_distances = [0] * jumlah_semua_semut
    current_ant = 0

    # Fungsi untuk memperbarui rute saat ini dan jarak untuk semut yang dipilih
    def update_route(ant_index):
        ruangan_sekarang = 0  # Ruangan awal
        ruangan_tersedia = list(range(1, jumlah_ruangan))
        current_routes[ant_index] = [0]  # Menambahkan ruangan awal A ke solusi
        current_distances[ant_index] = 0

        while ruangan_tersedia:
            ruangan_selanjutnya = pilih_ruangan(ant_index, ruangan_sekarang, ruangan_tersedia)
            current_routes[ant_index].append(ruangan_selanjutnya)
            current_distances[ant_index] += jarak[ruangan_sekarang][ruangan_selanjutnya]

            ruangan_tersedia.remove(ruangan_selanjutnya)
            ruangan_sekarang = ruangan_selanjutnya

            st.write(f"Pasien {ant_index+1} Rute Saat Ini: {[chr(ruangan + ord('A')) for ruangan in current_routes[ant_index]]}")

        current_distances[ant_index] += jarak[ruangan_sekarang][0]  # Kembali ke ruangan A
        current_routes[ant_index].append(0)  # Menambahkan ruangan A ke solusi

        st.write(f"Pasien {ant_index+1} Rute Akhir: {[chr(ruangan + ord('A')) for ruangan in current_routes[ant_index]]}")
        st.write(f"Pasien {ant_index+1} Jarak: {current_distances[ant_index]}")
        st.write("---")

    # Perbarui rute saat tombol yang sesuai diklik
    for i in range(jumlah_semua_semut):
        if ant_buttons[i]:
            update_route(i)
    st.markdown("---")
    st.caption("Developed by bunga")
    
#### ----- SECTION INPUT ---- ####
elif selected == "Input":
    st.header("Kalkulasi Optimasi Jarak Antar Ruangan")
    
     #-------------  INPUTAN PENGGUNA  -------------------
    jumlah_semua_semut = st.number_input("Jumlah Pasien", min_value=1, step=1, value=2)
    jumlah_ruangan = st.number_input("Jumlah Ruangan", min_value=1, step=1, value=2)

    # Membaca input jarak dari pengguna
    jarak = np.zeros((jumlah_ruangan, jumlah_ruangan))

    for i in range(jumlah_ruangan):
        for j in range(i + 1, jumlah_ruangan):
            jarak[i][j] = st.number_input(f"Masukkan jarak antara ruangan {i+1} dan ruangan {j+1}: ")
            jarak[j][i] = jarak[i][j]

    # Membaca input jumlah semut dari pengguna
    jumlah_semua_semut = st.number_input("Masukkan jumlah pasien: ", min_value=1, step=1)

    # Inisialisasi feromon
    feromon = np.ones((jumlah_ruangan, jumlah_ruangan))

    # Fungsi untuk memilih ruangan selanjutnya berdasarkan probabilitas
    def pilih_ruangan(semut, ruangan_sekarang, ruangan_tersedia):
        probabilitas = []

        for ruangan in ruangan_tersedia:
            pembilang = (feromon[ruangan_sekarang][ruangan] ** alpha) * ((1.0 / jarak[ruangan_sekarang][ruangan]) ** beta)
            penyebut = 0

            for r in ruangan_tersedia:
                penyebut += (feromon[ruangan_sekarang][r] ** alpha) * ((1.0 / jarak[ruangan_sekarang][r]) ** beta)

            probabilitas.append(pembilang / penyebut)

        total_probabilitas = sum(probabilitas)
        probabilitas = [p / total_probabilitas for p in probabilitas]
        ruangan_selanjutnya = random.choices(ruangan_tersedia, probabilitas)[0]

        return ruangan_selanjutnya

    # Fungsi untuk mengupdate feromon setiap siklus
    def update_feromon():
        for i in range(jumlah_ruangan):
            for j in range(jumlah_ruangan):
                if i != j:
                    feromon[i][j] *= pho

    # Algoritma koloni semut
    solusi_terbaik = []
    jarak_terbaik = float('inf')

    for siklus in range(NCmax):
        solusi = [[] for _ in range(jumlah_semua_semut)]
        jarak_semut = [0] * jumlah_semua_semut

        for semut in range(jumlah_semua_semut):
            ruangan_sekarang = 0  # Ruangan awal
            ruangan_tersedia = list(range(1, jumlah_ruangan))
            solusi_semut = [0]  # Menambahkan ruangan awal A ke solusi

            while ruangan_tersedia:
                ruangan_selanjutnya = pilih_ruangan(semut, ruangan_sekarang, ruangan_tersedia)
                solusi_semut.append(ruangan_selanjutnya)
                jarak_semut[semut] += jarak[ruangan_sekarang][ruangan_selanjutnya]

                ruangan_tersedia.remove(ruangan_selanjutnya)
                ruangan_sekarang = ruangan_selanjutnya

            jarak_semut[semut] += jarak[ruangan_sekarang][0]  # Kembali ke ruangan awal

            solusi[semut] = solusi_semut

            if jarak_semut[semut] < jarak_terbaik:
                solusi_terbaik = solusi_semut
                jarak_terbaik = jarak_semut[semut]

            # Update feromon
            for i in range(jumlah_ruangan):
                for j in range(jumlah_ruangan):
                    if i != j:
                        feromon[i][j] *= (1 - pho)
                        feromon[i][j] += pho / jarak_semut[semut]

        # Tampilkan solusi terbaik setiap siklus
        st.write(f"Siklus {siklus+1}: Solusi terbaik = {solusi_terbaik}, Jarak terbaik = {jarak_terbaik}")
        
     #-------------  TAMPIL SOLUSI DAN JARAK  -------------------
    # Tampilkan solusi terbaik dan jarak terbaik pada akhir iterasi
    st.write("Solusi terbaik:", solusi_terbaik)
    st.write("Jarak terbaik:", jarak_terbaik)
    
    
     #-------------  BUAT VISUALI RUTE  -------------------
    # Membuat diagram grafik menggunakan Graphviz
    graph = Digraph()

    for i in range(jumlah_ruangan):
        graph.node(str(i), label=f"Ruangan {i+1}")

    for i in range(len(solusi_terbaik) - 1):
        ruangan_saat_ini = solusi_terbaik[i]
        ruangan_selanjutnya = solusi_terbaik[i+1]
        graph.edge(str(ruangan_saat_ini), str(ruangan_selanjutnya))

    # Menampilkan diagram grafik menggunakan st.graphviz_chart
    st.graphviz_chart(graph.source)
    st.markdown("---")
    st.caption("Developed by bunga")
    

