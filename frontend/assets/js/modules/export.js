/**
 * export.js - Export Module
 * Exportación de datos
 */
const exporter = {
    download(type, format) {
        const url = `/api/v1/export/${type}?format=${format}`;
        
        if (format === 'json') {
            window.open(url, '_blank');
        } else {
            const a = document.createElement('a');
            a.href = url;
            a.download = `${type}_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
        
        toast.success('Descarga iniciada');
    }
};
