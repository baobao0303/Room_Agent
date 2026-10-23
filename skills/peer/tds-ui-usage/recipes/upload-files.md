## Upload File

**Use case:** Upload file với nhiều chế độ: button upload, drag-and-drop, picture wall. Sử dụng `customRequest` để gọi API upload.

**Components cần import:**
```typescript
import { TDSUploadModule } from 'tds-ui/upload';
import { TDSButtonModule } from 'tds-ui/button';
import { TDSMessageService } from 'tds-ui/message';
```

---

### 1. Upload bằng Button (mặc định)

```html
<tds-upload [fileList]="fileList">
  <button tds-button color="secondary">
    <span class="flex items-center">
      <i class="tdsi-upload-fill text-lg leading-none mr-2"></i>Upload
    </span>
  </button>
</tds-upload>
```

```typescript
import { Component } from '@angular/core';
import { TDSUploadFile } from 'tds-ui/upload';

@Component({
  selector: 'app-upload-basic',
  templateUrl: './upload-basic.component.html'
})
export class UploadBasicComponent {
  fileList: TDSUploadFile[] = [
    {
      uid: '1',
      name: 'document.pdf',
      status: 'done',
      url: 'https://example.com/document.pdf',
    },
    {
      uid: '2',
      name: 'photo.png',
      status: 'error',
      response: 'Upload failed',
    },
  ];
}
```

---

### 2. Upload Drag-and-Drop với customRequest

```html
<tds-upload
  type="drag"
  [multiple]="true"
  (uploadChange)="handleChange($event)"
  [customRequest]="handleUpload">
  <div class="w-full h-full p-4 border border-dashed border-neutral-2-200 rounded">
    <div class="flex items-center flex-col">
      <span class="tdsi-upload-fill text-3xl text-neutral-1-500"></span>
      <div class="text-neutral-1-900">
        Kéo thả file hoặc nhấn để chọn
      </div>
    </div>
  </div>
</tds-upload>
```

```typescript
import { HttpClient, HttpRequest, HttpResponse } from '@angular/common/http';
import { Component } from '@angular/core';
import { TDSMessageService } from 'tds-ui/message';
import { TDSSafeAny } from 'tds-ui/shared/utility';
import { TDSUploadChangeParam } from 'tds-ui/upload';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-upload-drag',
  templateUrl: './upload-drag.component.html'
})
export class UploadDragComponent {
  constructor(
    private msg: TDSMessageService,
    private http: HttpClient
  ) {}

  handleChange(info: TDSUploadChangeParam): void {
    if (info.file.status === 'done') {
      this.msg.success(`${info.file.name} upload thành công`);
    } else if (info.file.status === 'error') {
      this.msg.error(`${info.file.name} upload thất bại`);
    }
  }

  handleUpload = (item: any) => {
    const formData = new FormData();
    formData.append('file', item.file as any, item.file.name);

    const req = new HttpRequest('POST', '/api/upload', formData);
    return this.http
      .request(req)
      .pipe(filter(e => e instanceof HttpResponse))
      .subscribe(
        (res: TDSSafeAny) => {
          item.onSuccess(res.body, item.file);
        },
        (err) => {
          item.onError({ statusText: err.error?.message }, item.file);
        }
      );
  }
}
```

---

### 3. Upload Picture Wall (ảnh thumbnails)

```html
<tds-upload
  listType="picture-card"
  [(fileList)]="fileList"
  [showButton]="fileList.length < 8"
  [preview]="handlePreview"
  [customRequest]="handleUpload">
  <div class="w-full text-neutral-1-300">
    <div class="flex items-center justify-center">
      <span class="tdsi-images-fill text-xl leading-5"></span>
    </div>
    <div class="mt-2 text-body-2 font-regular">Upload</div>
  </div>
</tds-upload>

<tds-modal
  [visible]="previewVisible"
  [content]="modalContent"
  [footer]="null"
  (onCancel)="previewVisible = false">
  <ng-template #modalContent>
    <img [src]="previewImage" [ngStyle]="{ width: '100%' }" />
  </ng-template>
</tds-modal>
```

```typescript
import { Component } from '@angular/core';
import { TDSUploadFile } from 'tds-ui/upload';

const getBase64 = (file: File): Promise<string | ArrayBuffer | null> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
  });

@Component({
  selector: 'app-upload-picture-wall',
  templateUrl: './upload-picture-wall.component.html'
})
export class UploadPictureWallComponent {
  fileList: TDSUploadFile[] = [];
  previewImage: string = '';
  previewVisible = false;

  handlePreview = async (file: TDSUploadFile) => {
    if (!file.url && !file['preview']) {
      file['preview'] = await getBase64(file.originFileObj!);
    }
    this.previewImage = file.url || file['preview'];
    this.previewVisible = true;
  };

  handleUpload = (item: any) => {
    // Same as drag-and-drop example
  }
}
```

---

**Tips:**
- `type="select"` (mặc định) — hiển thị nút upload, `type="drag"` — vùng kéo thả
- `listType`: `"text"` (mặc định), `"picture"`, `"picture-card"` (ảnh thumbnail)
- Dùng `[customRequest]` để gọi API upload, bắt buộc dùng arrow function `= (item) => {}`
- `item.onSuccess(body, file)` — báo thành công, `item.onError(err, file)` — báo lỗi
- `[showButton]="fileList.length < N"` — ẩn nút upload khi đủ số lượng
- `[accept]` — giới hạn loại file (VD: `".png,.jpg,.pdf"`)
- `[size]` — giới hạn dung lượng (KB), `[fileType]` — giới hạn MIME type
- `[limit]` — giới hạn số file, `[multiple]="true"` — cho chọn nhiều file
- `(uploadChange)` — event khi trạng thái file thay đổi (uploading/done/error)
