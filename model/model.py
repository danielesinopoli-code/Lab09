import copy

from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()



    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """
        relazioni = TourDAO.get_tour_attrazioni()  # Restituisce lista di {id_tour, id_attrazione}

        if not relazioni:
            return

        for row in relazioni:
            t_id = row["id_tour"]
            a_id = row["id_attrazione"]

            if t_id in self.tour_map and a_id in self.attrazioni_map:
                tour_obj = self.tour_map[t_id]
                attr_obj = self.attrazioni_map[a_id]

                # Aggiungo l'oggetto attrazione al set del tour
                tour_obj.attrazioni.add(attr_obj)
                # (Opzionale) Aggiungo il tour all'attrazione



    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1
        tour_disponibili= []
        for tour in self.tour_map.values():
            if tour.id_regione == id_regione:
                tour_disponibili.append(tour)
        self._ricorsione(0,[],tour_disponibili,max_giorni,max_budget,0,set())



        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, tour_disponibili, giorni_rimanenti: int,
                    budget_rimanente: float, valore_corrente: int, attrazioni_usate: set):

        # 1. Aggiornamento del Massimo (
        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = copy.deepcopy(pacchetto_parziale)
            self._costo = sum(t.costo for t in pacchetto_parziale)


        for i in range(start_index, len(tour_disponibili)):
            tour_corrente = tour_disponibili[i]

            # --- CHECK VINCOLI ---

            # Check Budget
            if budget_rimanente is not None and tour_corrente.costo > budget_rimanente:
                continue

            # Check Giorni
            if giorni_rimanenti is not None and tour_corrente.durata_giorni > giorni_rimanenti:
                continue

            # Check Duplicati Attrazioni
            if not tour_corrente.attrazioni.isdisjoint(attrazioni_usate):
                continue



            # Calcolo i valori per il prossimo passo
            valore_tour = sum(attr.valore_culturale for attr in tour_corrente.attrazioni)


            nuovo_valore = valore_corrente + valore_tour


            nuovi_giorni = giorni_rimanenti - tour_corrente.durata_giorni if giorni_rimanenti is not None else None
            nuovo_budget = budget_rimanente - tour_corrente.costo if budget_rimanente is not None else None

            nuove_attrazioni = attrazioni_usate.union(tour_corrente.attrazioni)

            pacchetto_parziale.append(tour_corrente)


            self._ricorsione(
                i + 1,
                pacchetto_parziale,
                tour_disponibili,
                nuovi_giorni,
                nuovo_budget,
                nuovo_valore,
                nuove_attrazioni
            )

            # --- BACKTRACKING ---
            pacchetto_parziale.pop()






