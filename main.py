import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any

# --- Environment and App Setup ---
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL")

if not API_KEY or not API_URL:
    raise RuntimeError("API_KEY and API_URL must be set in .env file")

app = FastAPI(
    title="MaStR Proxy API",
    description="A robust proxy for the Marktstammdatenregister API with detailed documentation."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
#              REQUEST MODELS
# ==========================================

class EinheitRequest(BaseModel):
    marktakteur_mastr_nummer: str = Field(..., alias="marktakteurMastrNummer")
    einheit_mastr_nummer: str = Field(..., alias="einheitMastrNummer")
    model_config = ConfigDict(populate_by_name=True)

class GetListeAlleNetzanschlusspunkteRequest(BaseModel):
    marktakteur_mastr_nummer: str = Field(..., alias="marktakteurMastrNummer")
    start_ab: Optional[int] = Field(None, alias="startAb")
    datum_ab: Optional[str] = Field(None, alias="datumAb")
    limit_param: Optional[int] = Field(None, alias="limit")
    einheit_art: Optional[str] = Field(None, alias="Einheitart")
    einheit_typ: Optional[str] = Field(None, alias="Einheittyp")
    einheit_postleitzahl: Optional[str] = Field(None, alias="EinheitPostleitzahl")
    einheit_ort: Optional[str] = Field(None, alias="EinheitOrt")
    einheit_gemeinde: Optional[str] = Field(None, alias="EinheitGemeinde")
    einheit_gemeindeschluessel: Optional[str] = Field(None, alias="EinheitGemeindeschluessel")
    regel_zone: Optional[str] = Field(None, alias="Regelzone")
    name_der_technischen_lokation: Optional[str] = Field(None, alias="NameDerTechnischenLokation")
    netzbetreiber_mastr_nummer: Optional[str] = Field(None, alias="NetzbetreiberMastrNummer")
    netzanschlusspunkt_bezeichnung: Optional[str] = Field(None, alias="NetzanschlusspunktBezeichnung")
    messlokation: Optional[str] = Field(None, alias="Messlokation")
    spannungs_ebene: Optional[str] = Field(None, alias="Spannungsebene")
    nettoengpass_leistung: Optional[float] = Field(None, alias="Nettoengpassleistung")
    netzanschluss_kapazitaet: Optional[float] = Field(None, alias="Netzanschlusskapazitaet")
    maximale_einspeiseleistung: Optional[float] = Field(None, alias="MaximaleEinspeiseleistung")
    maximale_ausspeiseleistung: Optional[float] = Field(None, alias="MaximaleAusspeiseleistung")
    gas_qualitaet: Optional[str] = Field(None, alias="Gasqualitaet")
    geplanter_netzanschlusspunkt: Optional[bool] = Field(None, alias="GeplanterNetzanschlusspunkt")
    yeic: Optional[str] = Field(None, alias="Yeic")
    einheit_mastr_nummer_list: Optional[List[str]] = Field(None, alias="einheitMastrNummer")
    netzanschlusspunkt_mastr_nummer_list: Optional[List[str]] = Field(None, alias="NetzanschlusspunktMastrNummer")
    lokation_mastr_nummer_list: Optional[List[str]] = Field(None, alias="LokationMastrNummer")
    model_config = ConfigDict(populate_by_name=True)


# ==========================================
#              RESPONSE MODELS
# ==========================================

# --- Base Model for all GetEinheit... Responses ---
class BaseEinheitResponse(BaseModel):
    ergebniscode: str = Field(..., alias="Ergebniscode")
    aufruf_veraltet: bool = Field(..., alias="AufrufVeraltet")
    aufruf_lebenszeit_ende: Optional[str] = Field(None, alias="AufrufLebenszeitEnde")
    aufruf_version: int = Field(..., alias="AufrufVersion")
    einheit_mastr_nummer: str = Field(..., alias="EinheitMastrNummer")
    datum_letzte_aktualisierung: str = Field(..., alias="DatumLetzteAktualisierung")
    lokation_mastr_nummer: Optional[str] = Field(None, alias="LokationMastrNummer")
    netzbetreiberpruefung_status: str = Field(..., alias="NetzbetreiberpruefungStatus")
    netzbetreiberzuordnungen: Optional[List[str]] = Field(None, alias="Netzbetreiberzuordnungen[]")
    netzbetreiberpruefung_datum: Optional[str] = Field(None, alias="NetzbetreiberpruefungDatum")
    anlagenbetreiber_mastr_nummer: Optional[str] = Field(None, alias="AnlagenbetreiberMastrNummer")
    land: str = Field(..., alias="Land")
    bundesland: Optional[str] = Field(None, alias="Bundesland")
    landkreis: Optional[str] = Field(None, alias="Landkreis")
    gemeinde: Optional[str] = Field(None, alias="Gemeinde")
    gemeindeschluessel: Optional[str] = Field(None, alias="Gemeindeschluessel")
    postleitzahl: str = Field(..., alias="Postleitzahl")
    gemarkung: Optional[str] = Field(None, alias="Gemarkung")
    flur_flurstuecknummern: Optional[str] = Field(None, alias="FlurFlurstuecknummern")
    strasse: Optional[str] = Field(None, alias="Strasse")
    strasse_nicht_gefunden: Optional[bool] = Field(None, alias="StrasseNichtGefunden")
    hausnummer: Optional[str] = Field(None, alias="Hausnummer")
    hausnummer_nicht_gefunden: Optional[bool] = Field(None, alias="HausnummerNichtGefunden")
    adresszusatz: Optional[str] = Field(None, alias="Adresszusatz")
    ort: str = Field(..., alias="Ort")
    laengengrad: Optional[float] = Field(None, alias="Laengengrad")
    breitengrad: Optional[float] = Field(None, alias="Breitengrad")
    utm_zonenwert: Optional[int] = Field(None, alias="UtmZonenwert")
    utm_east: Optional[float] = Field(None, alias="UtmEast")
    utm_north: Optional[float] = Field(None, alias="UtmNorth")
    gauss_krueger_hoch: Optional[float] = Field(None, alias="GaussKruegerHoch")
    gauss_krueger_rechts: Optional[float] = Field(None, alias="GaussKruegerRechts")
    registrierungsdatum: Optional[str] = Field(None, alias="Registrierungsdatum")
    geplantes_inbetriebnahmedatum: Optional[str] = Field(None, alias="GeplantesInbetriebnahmedatum")
    inbetriebnahmedatum: Optional[str] = Field(None, alias="Inbetriebnahmedatum")
    datum_endgueltige_stilllegung: Optional[str] = Field(None, alias="DatumEndgueltigeStilllegung")
    datum_beginn_voruebergehende_stilllegung: Optional[str] = Field(None, alias="DatumBeginnVoruebergehendeStilllegung")
    datum_wiederaufnahme_betrieb: Optional[str] = Field(None, alias="DatumWiederaufnahmeBetrieb")
    einheit_systemstatus: Optional[str] = Field(None, alias="EinheitSystemstatus")
    einheit_betriebsstatus: str = Field(..., alias="EinheitBetriebsstatus")
    bestandsanlage_mastr_nummer: Optional[str] = Field(None, alias="BestandsanlageMastrNummer")
    nicht_vorhanden_in_migrierten_einheiten: Optional[bool] = Field(None, alias="NichtVorhandenInMigriertenEinheiten")
    alt_anlagenbetreiber_mastr_nummer: Optional[str] = Field(None, alias="AltAnlagenbetreiberMastrNummer")
    datum_des_betreiberwechsels: Optional[str] = Field(None, alias="DatumDesBetreiberwechsels")
    datum_registrierung_des_betreiberwechsels: Optional[str] = Field(None, alias="DatumRegistrierungDesBetreiberwechsels")
    inbetriebnahmedatum_am_aktuellen_ort: Optional[str] = Field(None, alias="InbetriebnahmedatumAmAktuellenOrt")
    name_stromerzeugungseinheit: str = Field(..., alias="NameStromerzeugungseinheit")
    weic: Optional[str] = Field(None, alias="Weic")
    weic_display_name: Optional[str] = Field(None, alias="WeicDisplayName")
    kraftwerksnummer: Optional[str] = Field(None, alias="Kraftwerksnummer")
    energietraeger: str = Field(..., alias="Energietraeger")
    bruttoleistung: float = Field(..., alias="Bruttoleistung")
    nettonennleistung: float = Field(..., alias="Nettonennleistung")
    schwarzstartfaehigkeit: Optional[bool] = Field(None, alias="Schwarzstartfaehigkeit")
    inselbetriebsfaehigkeit: Optional[bool] = Field(None, alias="Inselbetriebsfaehigkeit")
    einsatzverantwortlicher: Optional[str] = Field(None, alias="Einsatzverantwortlicher")
    fernsteuerbarkeit_nb: Optional[bool] = Field(None, alias="FernsteuerbarkeitNb")
    fernsteuerbarkeit_dv: Optional[bool] = Field(None, alias="FernsteuerbarkeitDv")
    einspeisungsart: Optional[str] = Field(None, alias="Einspeisungsart")
    praequalifiziert_fuer_regelenergie: Optional[bool] = Field(None, alias="PraequalifiziertFuerRegelenergie")
    gen_mastr_nummer: Optional[str] = Field(None, alias="GenMastrNummer")
    model_config = ConfigDict(populate_by_name=True)

# --- Specific Response Models ---
class GetEinheitWindResponse(BaseEinheitResponse):
    name_windpark: str = Field(..., alias="NameWindpark")
    wind_an_land_oder_see: str = Field(..., alias="WindAnLandOderSee")
    seelage: Optional[str] = Field(None, alias="Seelage")
    gebiet_nach_dem_flaechenentwicklungsplan_ostsee: Optional[str] = Field(None, alias="GebietNachDemFlaechenentwicklungsplanOstsee")
    gebiet_nach_dem_flaechenentwicklungsplan_nordsee: Optional[str] = Field(None, alias="GebietNachDemFlaechenentwicklungsplanNordsee")
    hersteller: Optional[str] = Field(None, alias="Hersteller")
    technologie: Optional[str] = Field(None, alias="Technologie")
    typenbezeichnung: str = Field(..., alias="Typenbezeichnung")
    nabenhoehe: Optional[float] = Field(None, alias="Nabenhoehe")
    rotordurchmesser: Optional[float] = Field(None, alias="Rotordurchmesser")
    rotorblattenteisungssystem: Optional[bool] = Field(None, alias="Rotorblattenteisungssystem")
    auflage_abschaltung_leistungsbegrenzung: Optional[bool] = Field(None, alias="AuflageAbschaltungLeistungsbegrenzung")
    auflagen_abschaltung_schallimmissionsschutz_nachts: Optional[bool] = Field(None, alias="AuflagenAbschaltungSchallimmissionsschutzNachts")
    auflagen_abschaltung_schallimmissionsschutz_tagsueber: Optional[bool] = Field(None, alias="AuflagenAbschaltungSchallimmissionsschutzTagsueber")
    auflagen_abschaltung_schattenwurf: Optional[bool] = Field(None, alias="AuflagenAbschaltungSchattenwurf")
    auflagen_abschaltung_tierschutz: Optional[bool] = Field(None, alias="AuflagenAbschaltungTierschutz")
    auflagen_abschaltung_eiswurf: Optional[bool] = Field(None, alias="AuflagenAbschaltungEiswurf")
    auflagen_abschaltung_sonstige: Optional[bool] = Field(None, alias="AuflagenAbschaltungSonstige")
    wassertiefe: Optional[float] = Field(None, alias="Wassertiefe")
    kuestenentfernung: Optional[float] = Field(None, alias="Kuestenentfernung")
    buergerenergie: Optional[bool] = Field(None, alias="Buergerenergie")
    nachtkennzeichen: Optional[bool] = Field(None, alias="Nachtkennzeichen")
    eeg_mastr_nummer: Optional[str] = Field(None, alias="EegMastrNummer")
    technologie_flugwind: Optional[str] = Field(None, alias="TechnologieFlugwind")
    flughoehe: Optional[float] = Field(None, alias="Flughoehe")
    flugradius: Optional[float] = Field(None, alias="Flugradius")

class GetEinheitSolarResponse(BaseEinheitResponse):
    zugeordnete_wirkleistung_wechselrichter: Optional[float] = Field(None, alias="zugeordneteWirkleistungWechselrichter")
    anzahl_module: Optional[int] = Field(None, alias="AnzahlModule")
    art_der_solaranlage: Optional[str] = Field(None, alias="ArtDerSolaranlage")
    solaranlagen_kategorie: Optional[str] = Field(None, alias="SolaranlagenKategorie")
    leistungsbegrenzung: Optional[str] = Field(None, alias="Leistungsbegrenzung")
    einheitliche_ausrichtung_und_neigungswinkel: Optional[bool] = Field(None, alias="EinheitlicheAusrichtungUndNeigungswinkel")
    hauptausrichtung: Optional[str] = Field(None, alias="Hauptausrichtung")
    hauptausrichtung_neigungswinkel: Optional[str] = Field(None, alias="HauptausrichtungNeigungswinkel")
    nebenausrichtung: Optional[str] = Field(None, alias="Nebenausrichtung")
    nebenausrichtung_neigungswinkel: Optional[str] = Field(None, alias="NebenausrichtungNeigungswinkel")
    groesse_der_in_anspruch_genommenen_flaeche: Optional[float] = Field(None, alias="GroesseDerInAnspruchGenommenenFlaeche")
    ueberwiegende_nutzungsart_der_flaeche_vor_errichtung_der_solaranlage: Optional[str] = Field(None, alias="UeberwiegendeNutzungsartDerFlaecheVorErrichtungDerSolaranlage")
    vorheriger_nutzungsartenbereich_der_flaeche: Optional[str] = Field(None, alias="VorherigerNutzungsartenbereichDerFlaeche")
    zusaetzliche_merkmale_der_flaeche_und_aktuellen_flaechennutzung: Optional[List[str]] = Field(None, alias="ZusaetzlicheMerkmaleDerFlaecheUndAktuellenFlaechennutzung[]")
    lichte_hoehe: Optional[float] = Field(None, alias="LichteHoehe")
    nutzungsbereich: Optional[str] = Field(None, alias="Nutzungsbereich")
    buergerenergie: Optional[bool] = Field(None, alias="Buergerenergie")
    zaehlernummer: Optional[str] = Field(None, alias="Zaehlernummer")
    eeg_mastr_nummer: Optional[str] = Field(None, alias="EegMastrNummer")
    speicher_am_gleichen_ort: Optional[bool] = Field(None, alias="SpeicherAmGleichenOrt")
    name_des_solarparks: Optional[str] = Field(None, alias="NameDesSolarparks")

class GetEinheitBiomasseResponse(BaseEinheitResponse):
    hauptbrennstoff: Optional[str] = Field(None, alias="Hauptbrennstoff")
    biomasseart: Optional[str] = Field(None, alias="Biomasseart")
    technologie: str = Field(..., alias="Technologie")
    eeg_mastr_nummer: str = Field(..., alias="EegMastrNummer")
    kwk_mastr_nummer: Optional[str] = Field(None, alias="KwkMastrNummer")
    netzreserve_zugeordnet: Optional[bool] = Field(None, alias="NetzreserveZugeordnet")
    datum_netzreserve: Optional[str] = Field(None, alias="DatumNetzreserve")
    kapazitaetsreserve_zugeordnet: Optional[bool] = Field(None, alias="KapazitaetsreserveZugeordnet")
    datum_kapazitaetsreserve: Optional[str] = Field(None, alias="DatumKapazitaetsreserve")

class GetEinheitStromSpeicherResponse(BaseEinheitResponse):
    einsatzort: Optional[str] = Field(None, alias="Einsatzort")
    ac_dc_koppelung: Optional[str] = Field(None, alias="AcDcKoppelung")
    batterietechnologie: Optional[str] = Field(None, alias="Batterietechnologie")
    leistungsaufnahme_beim_einspeichern: Optional[float] = Field(None, alias="LeistungsaufnahmeBeimEinspeichern")
    pumpbetrieb_kontinuierlich_regelbar: Optional[bool] = Field(None, alias="PumpbetriebKontinuierlichRegelbar")
    pumpspeichertechnologie: Optional[str] = Field(None, alias="Pumpspeichertechnologie")
    notstromaggregat: Optional[bool] = Field(None, alias="Notstromaggregat")
    bestandteil_grenzkraftwerk: Optional[bool] = Field(None, alias="BestandteilGrenzkraftwerk")
    nettonennleistung_deutschland: Optional[float] = Field(None, alias="NettonennleistungDeutschland")
    zugeordnete_wirkleistung_wechselrichter: Optional[float] = Field(None, alias="ZugeordneteWirkleistungWechselrichter")
    nutzbare_speicherkapazitaet: Optional[float] = Field(None, alias="NutzbareSpeicherkapazitaet")
    spe_mastr_nummer: Optional[str] = Field(None, alias="SpeMastrNummer")
    eeg_mastr_nummer: Optional[str] = Field(None, alias="EegMastrNummer")
    eeg_anlagentyp: Optional[str] = Field(None, alias="EegAnlagentyp")
    technologie: Optional[str] = Field(None, alias="Technologie")
    netzreserve_zugeordnet: Optional[bool] = Field(None, alias="NetzreserveZugeordnet")
    datum_netzreserve: Optional[str] = Field(None, alias="DatumNetzreserve")
    kapazitaetsreserve_zugeordnet: Optional[bool] = Field(None, alias="KapazitaetsreserveZugeordnet")
    datum_kapazitaetsreserve: Optional[str] = Field(None, alias="DatumKapazitaetsreserve")
    gemeinsam_registrierte_solareinheit_mastr_nummer: Optional[str] = Field(None, alias="GemeinsamRegistrierteSolareinheitMastrNummer")

# Response for GetListeAlleNetzanschlusspunkte
class GetListeAlleNetzanschlusspunkteResponse(BaseModel):
    ergebniscode: str = Field(..., alias="Ergebniscode")
    aufruf_veraltet: bool = Field(..., alias="AufrufVeraltet")
    aufruf_lebenszeit_ende: Optional[str] = Field(None, alias="AufrufLebenszeitEnde")
    aufruf_version: int = Field(..., alias="AufrufVersion")
    # Note: The schema provided shows "ListeNetzanschlusspunkte[]".
    # The type inside the list would need its own model if detailed documentation is required for it.
    # For now, using List[Dict[str, Any]] to represent the list of objects.
    liste_netzanschlusspunkte: Optional[List[Dict[str, Any]]] = Field(None, alias="ListeNetzanschlusspunkte[]")
    model_config = ConfigDict(populate_by_name=True)


# ==========================================
#              API LOGIC & ENDPOINTS
# ==========================================

def call_external_api(endpoint: str, request_data: BaseModel) -> Dict[str, Any]:
    """Calls the external API and returns the raw JSON."""
    url = f"{API_URL}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    # Convert request model to PascalCase JSON
    payload = request_data.model_dump(by_alias=True, exclude_none=True)
    payload['apiKey'] = API_KEY

    # Handle '[]' suffix for specific list keys in the request
    for key in ["einheitMastrNummer", "NetzanschlusspunktMastrNummer", "LokationMastrNummer"]:
        if key in payload and isinstance(payload[key], list):
            payload[f"{key}[]"] = payload.pop(key)

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        safe_payload = {k: v for k, v in payload.items() if k != 'apiKey'}
        error_detail = f"External API Error ({response.status_code}): {response.text} | Sent Payload: {safe_payload}"
        raise HTTPException(status_code=response.status_code, detail=error_detail)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to external API: {e}")

# Use response_model and response_model_by_alias=True to ensure 
# the output is validated and documented with PascalCase keys.

@app.post("/get_einheit_biomasse", summary="Get Einheit Biomasse", response_model=GetEinheitBiomasseResponse, response_model_by_alias=True)
def get_einheit_biomasse_proxy(request: EinheitRequest):
    return call_external_api("GetEinheitBiomasse", request)

@app.post("/get_einheit_solar", summary="Get Einheit Solar", response_model=GetEinheitSolarResponse, response_model_by_alias=True)
def get_einheit_solar_proxy(request: EinheitRequest):
    return call_external_api("GetEinheitSolar", request)

@app.post("/get_einheit_wind", summary="Get Einheit Wind", response_model=GetEinheitWindResponse, response_model_by_alias=True)
def get_einheit_wind_proxy(request: EinheitRequest):
    return call_external_api("GetEinheitWind", request)

@app.post("/get_einheit_strom_speicher", summary="Get Einheit Strom Speicher", response_model=GetEinheitStromSpeicherResponse, response_model_by_alias=True)
def get_einheit_strom_speicher_proxy(request: EinheitRequest):
    return call_external_api("GetEinheitStromSpeicher", request)

@app.post("/get_liste_alle_netzanschlusspunkte", summary="Get Liste Alle Netzanschlusspunkte", response_model=GetListeAlleNetzanschlusspunkteResponse, response_model_by_alias=True)
def get_liste_alle_netzanschlusspunkte_proxy(request: GetListeAlleNetzanschlusspunkteRequest):
    return call_external_api("GetListeAlleNetzanschlusspunkte", request)

@app.get("/", summary="API Root", include_in_schema=False)
async def root():
    return {"message": "Welcome to the MaStR Proxy API! Visit /docs for documentation."}