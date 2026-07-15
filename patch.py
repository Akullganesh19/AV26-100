import re

with open("frontend/src/pages/DiagnosticsCenter.tsx", "r") as f:
    content = f.read()

# Replace axios with apiClient
content = content.replace("import axios from 'axios';", "import { apiClient } from '../api/client';\nimport { useEffect } from 'react';")
content = content.replace("axios.post(`${import.meta.env.VITE_API_URL}/clinical/${activeTab}`", "apiClient.post(`/clinical/${activeTab}`")
content = content.replace("axios.post(\n        `${import.meta.env.VITE_API_URL}/clinical/report`", "apiClient.post(\n        '/clinical/report'")

# Add prefetch state
content = content.replace(
    "const [prediction, setPrediction] = useState<any>(null);",
    "const [prediction, setPrediction] = useState<any>(null);\n  const [prefetchUrl, setPrefetchUrl] = useState<string | null>(null);"
)

# Reset prefetch url on form submit
content = content.replace(
    "setPrediction(null);",
    "setPrediction(null);\n    setPrefetchUrl(null);"
)

# Add useEffect for prefetching
use_effect_code = """
  // 🛸 Oracle: Predictive Intelligence
  // Prediction: User will download the report after seeing the diagnosis.
  // Data: The diagnosis result.
  // Action: Prefetch the PDF in the background so download is instant.
  useEffect(() => {
    let localBlobUrl: string | null = null;

    if (prediction) {
      const prefetchReport = async () => {
        try {
          const response = await apiClient.post(
            '/clinical/report',
            [prediction],
            { responseType: 'blob' }
          );
          localBlobUrl = window.URL.createObjectURL(new Blob([response.data]));
          setPrefetchUrl(localBlobUrl);
        } catch (error) {
          console.error('Prefetching report failed:', error);
        }
      };

      prefetchReport();
    }

    return () => {
      if (localBlobUrl) {
        window.URL.revokeObjectURL(localBlobUrl);
      }
    };
  }, [prediction]);
"""

content = content.replace(
    "const handleDownloadReport = async () => {",
    f"{use_effect_code}\n  const handleDownloadReport = async () => {{"
)

# Modify handleDownloadReport
new_download = """const handleDownloadReport = async () => {
    if (!prediction) return;

    // 🛸 Oracle: Use pre-computed report if ready
    if (prefetchUrl) {
      const link = document.createElement('a');
      link.href = prefetchUrl;
      link.setAttribute('download', `EpiSense_Tactical_Report_${activeTab.toUpperCase()}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Report downloaded instantly');
      return;
    }

    // Fallback if prediction is wrong or user clicked too fast
    try {
      const response = await apiClient.post(
        '/clinical/report',
        [prediction], // Send current prediction in a list
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `EpiSense_Tactical_Report_${activeTab.toUpperCase()}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      // Revoke the fallback URL immediately
      window.setTimeout(() => window.URL.revokeObjectURL(url), 100);
      toast.success('Report generated successfully');
    } catch (error) {
      console.error('Report generation failed:', error);
      toast.error('Failed to generate PDF report');
    }
  };"""

content = re.sub(
    r"const handleDownloadReport = async \(\) => \{[\s\S]*?toast\.error\('Failed to generate PDF report'\);\n    \}\n  \};",
    new_download,
    content
)


with open("frontend/src/pages/DiagnosticsCenter.tsx", "w") as f:
    f.write(content)
