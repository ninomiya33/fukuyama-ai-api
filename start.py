#!/usr/bin/env python3
"""
Render用の起動スクリプト
"""

import os
import uvicorn
from api import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
