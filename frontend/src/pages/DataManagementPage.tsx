import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { AppDispatch, RootState } from '@/store'
import {
	fetchData,
	uploadData,
	validateData,
	deleteData,
	clearError,
	clearValidation,
} from '@/store/dataSlice'

const datasetTypes: { key: string; label: string }[] = [
	{ key: 'warehouses', label: 'Warehouses' },
	{ key: 'customers', label: 'Customers' },
	{ key: 'routes', label: 'Routes' },
]

const DataManagementPage = () => {
	const dispatch = useDispatch<AppDispatch>()
	const { warehouses, customers, routes, loading, error, validation } = useSelector((s: RootState) => s.data)
	const [selectedFiles, setSelectedFiles] = useState<Record<string, File | null>>({})

	useEffect(() => {
		dispatch(fetchData())
	}, [dispatch])

	const handleFileChange = (dataType: string, fileList: FileList | null) => {
		if (!fileList || !fileList[0]) return
		setSelectedFiles((prev) => ({ ...prev, [dataType]: fileList[0] }))
	}

	const handleUpload = (dataType: string) => {
		const file = selectedFiles[dataType]
		if (!file) return
		dispatch(uploadData({ file, dataType }))
	}

	const handleValidate = () => {
		dispatch(
			validateData({
				warehouses,
				customers,
				routes,
			})
		)
	}

	const handleDelete = (dataType: string) => {
		dispatch(deleteData(dataType))
	}

	return (
		<div className="p-6 space-y-8">
			<div className="flex items-center justify-between">
				<h1 className="text-2xl font-semibold">Data Management</h1>
				<button
					onClick={() => dispatch(fetchData())}
					className="px-4 py-2 rounded bg-indigo-600 text-white text-sm hover:bg-indigo-500 disabled:opacity-50"
					disabled={loading}
				>
					Refresh
				</button>
			</div>

			{error && (
				<div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded flex items-start justify-between">
					<div>
						<p className="font-medium">Error</p>
						<p className="text-sm">{error}</p>
					</div>
					<button onClick={() => dispatch(clearError())} className="text-xs underline ml-4">
						Dismiss
					</button>
				</div>
			)}

			<div className="grid gap-6 md:grid-cols-3">
				{datasetTypes.map((ds) => {
					const count = ds.key === 'warehouses' ? warehouses.length : ds.key === 'customers' ? customers.length : routes.length
					const file = selectedFiles[ds.key]
					return (
						<div key={ds.key} className="border rounded p-4 space-y-3 bg-slate-800 shadow-sm border-slate-700">
							<div className="flex items-center justify-between">
								<h2 className="font-medium text-slate-200">{ds.label}</h2>
								<span className="text-xs px-2 py-0.5 rounded-full bg-slate-700 text-slate-300">{count} items</span>
							</div>
							<input
								type="file"
								accept=".csv,.json"
								onChange={(e) => handleFileChange(ds.key, e.target.files)}
								className="block w-full text-sm"
							/>
							{file && <p className="text-xs text-gray-500 truncate">{file.name}</p>}
							<div className="flex gap-2">
								<button
									onClick={() => handleUpload(ds.key)}
									disabled={!file || loading}
									className="flex-1 px-3 py-2 text-xs rounded bg-blue-600 text-white disabled:opacity-40"
								>
									Upload
								</button>
								<button
									onClick={() => handleDelete(ds.key)}
									disabled={loading || count === 0}
									className="px-3 py-2 text-xs rounded bg-red-600 text-white disabled:opacity-40"
								>
									Delete
								</button>
							</div>
						</div>
					)
				})}
			</div>

			<div className="space-y-4">
				<div className="flex items-center gap-3">
					<button
						onClick={handleValidate}
						disabled={loading}
						className="px-4 py-2 rounded bg-emerald-600 text-white text-sm hover:bg-emerald-500 disabled:opacity-50"
					>
						Validate Data
					</button>
					{validation && (
						<button
							onClick={() => dispatch(clearValidation())}
							className="text-xs underline text-gray-600"
						>
							Clear Validation
						</button>
					)}
				</div>
				{validation && (
					<div className="border rounded p-4 bg-white shadow-sm space-y-2">
						<h3 className="font-medium">Validation Result</h3>
						<p className={`text-sm ${validation.valid ? 'text-emerald-600' : 'text-red-600'}`}>
							{validation.valid ? 'All datasets passed validation.' : 'Issues detected in datasets.'}
						</p>
						{!!validation.errors?.length && (
							<div>
								<p className="text-xs font-semibold text-red-600">Errors</p>
								<ul className="list-disc ml-5 mt-1 space-y-0.5 text-xs text-red-600">
									{validation.errors.slice(0, 5).map((e, i) => (
										<li key={i}>{JSON.stringify(e)}</li>
									))}
									{validation.errors.length > 5 && <li>+{validation.errors.length - 5} more…</li>}
								</ul>
							</div>
						)}
						{!!validation.warnings?.length && (
							<div>
								<p className="text-xs font-semibold text-amber-600">Warnings</p>
								<ul className="list-disc ml-5 mt-1 space-y-0.5 text-xs text-amber-600">
									{validation.warnings.slice(0, 5).map((w, i) => (
										<li key={i}>{JSON.stringify(w)}</li>
									))}
									{validation.warnings.length > 5 && <li>+{validation.warnings.length - 5} more…</li>}
								</ul>
							</div>
						)}
					</div>
				)}
			</div>

			{loading && (
				<div className="fixed inset-0 bg-black/10 backdrop-blur-[1px] flex items-center justify-center">
					<div className="px-4 py-2 rounded bg-white shadow animate-pulse text-sm">Processing…</div>
				</div>
			)}
		</div>
	)
}

export default DataManagementPage
