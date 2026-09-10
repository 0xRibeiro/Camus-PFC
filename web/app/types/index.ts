import type { components } from './api'

type S = components['schemas']


// 

export type TrilhaRead = S['TrilhaRead']
export type TrilhaCreate = S['TrilhaCreate']
export type TrilhaUpdate = S['TrilhaUpdate']
export type TrilhaPage = S['Page_TrilhaRead_']

export type ModuloRead = S['ModuloRead']
export type ModuloCreate = S['ModuloCreate']
export type ModuloUpdate = S['ModuloUpdate']

export type ConteudoRead = S['ConteudoRead']
export type ConteudoCreate = S['ConteudoCreate']
export type ConteudoUpdate = S['ConteudoUpdate']
export type ConteudoTipo = S['ConteudoTipo']

export type QuestaoRead = S['QuestaoRead']
export type QuestaoCreate = S['QuestaoCreate']
export type QuestaoUpdate = S['QuestaoUpdate']

export type AlternativaRead = S['AlternativaRead']
export type AlternativaCreate = S['AlternativaCreate']
export type AlternativaUpdate = S['AlternativaUpdate']
