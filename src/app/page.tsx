'use client'

import { DocumentUploader } from '@/components/organisms/DocumentUploader'
import { QAInterface } from '@/components/organisms/QAInterface'
import { DocumentManager } from '@/components/organisms/DocumentManager'
import { FileSearch2, BrainCircuit, Mic } from "lucide-react"

export default function Home() {
  return (
    <div className="flex h-screen bg-gray-100">
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Mini Asistente Q&A</h2>
          <p className="text-xs text-gray-600 mb-3">
            Sube tus documentos en formato <span className="font-medium">PDF</span> o <span className="font-medium">TXT</span>. 
            Luego podrás hacer preguntas y elegir cómo deseas buscar:
          </p>

          <ul className="text-xs text-gray-600 space-y-2 mb-4">
            <li className="flex items-center gap-2">
              <FileSearch2 className="h-4 w-4 text-gray-700" />
              <span><span className="font-medium">Textual Search</span>: encuentra coincidencias exactas en el texto.</span>
            </li>
            <li className="flex items-center gap-2">
              <BrainCircuit className="h-4 w-4 text-gray-700" />
              <span><span className="font-medium">AI Reasoning Search</span>: interpreta el contexto y responde de forma razonada.</span>
            </li>
            <li className="flex items-center gap-2">
              <Mic className="h-4 w-4 text-gray-700" />
              <span><span className="font-medium">Micrófono</span>: activa el modo de dictado por voz (en desarrollo).</span>
            </li>
          </ul>

          <h3 className="text-sm font-medium text-gray-900 mb-3">Upload Documents</h3>
          <DocumentUploader />
        </div>

        <div className="flex-1 p-4 overflow-y-auto">
          <DocumentManager />
        </div>
      </div>

      <div className="flex-1 flex flex-col bg-gray-100">
        <div className="flex-1 flex flex-col justify-center p-8">
          <div className="w-full max-w-2xl mx-auto">
            <QAInterface />
          </div>
        </div>
      </div>
    </div>
  )
}
