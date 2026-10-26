# Upload

Component tải lên file với nhiều chế độ hiển thị và xử lý. Hỗ trợ drag-drop, preview, và custom request.

**Selector:** `tds-upload`
**Import:** `import { TDSUploadModule } from 'tds-ui/upload';`
**Export as:** `tdsUpload`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `TDSUploadType` | `'select'` | Loại upload: `select`, `drag` |
| `action` | `string \| function` | — | URL upload hoặc function trả về URL |
| `accept` | `string \| string[]` | — | File types được chấp nhận (MIME type hoặc extension) |
| `fileType` | `string` | — | Loại file (phân cách bằng dấu phẩy) |
| `beforeUpload` | `function` | — | Callback trước khi upload, return `false` để hủy |
| `customRequest` | `function` | — | Custom upload request (AJAX, axios, etc.) |
| `data` | `object \| function` | — | Dữ liệu gửi kèm request |
| `headers` | `object \| function` | — | Headers gửi kèm request |
| `name` | `string` | `'file'` | Tên field file trong request |
| `withCredentials` | `boolean` | `false` | Gửi credentials cross-site |
| `multiple` | `boolean` | `false` | Cho phép chọn nhiều file |
| `directory` | `boolean` | `false` | Chọn thư mục thay vì file |
| `disabled` | `boolean` | `false` | Vô hiệu hóa upload |
| `listType` | `TDSUploadListType` | `'text'` | Kiểu hiển thị: `text`, `picture`, `picture-card` |
| `fileList` | `TDSUploadFile[]` | `[]` | Danh sách file đang quản lý |
| `limit` | `number` | `0` | Giới hạn số lượng file (0 = unlimited) |
| `size` | `number` | `0` | Giới hạn kích thước file (KB) |
| `filter` | `UploadFilter[]` | `[]` | Custom filter rules |
| `showUploadList` | `boolean \| object` | `true` | Hiển thị danh sách file |
| `showButton` | `boolean` | `true` | Hiển thị nút upload |
| `isOpenFileDialogOnClick` | `boolean` | `true` | Mở file dialog khi click button |
| `remove` | `function` | — | Callback khi xóa file |
| `preview` | `function` | — | Callback khi preview file |
| `previewFile` | `function` | — | Custom preview file (return `Observable<string>`) |
| `previewIsImage` | `function` | — | Kiểm tra file có phải ảnh không |
| `transformFile` | `function` | — | Transform file trước khi upload |
| `download` | `function` | — | Callback khi download file |
| `iconRender` | `TemplateRef` | — | Custom icon render template |
| `fileListRender` | `TemplateRef` | — | Custom file list render template |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `uploadChange` | `EventEmitter<TDSUploadChangeParam>` | Khi trạng thái upload thay đổi |
| `fileListChange` | `EventEmitter<TDSUploadFile[]>` | Khi danh sách file thay đổi |

## TDSUploadFile structure

```typescript
interface TDSUploadFile {
  uid: string;              // Unique ID
  name: string;             // File name
  size?: number;            // File size (bytes)
  type?: string;            // MIME type
  url?: string;             // File URL
  status?: UploadFileStatus; // 'uploading' | 'done' | 'error' | 'success' | 'removed'
  percent?: number;         // Upload progress (0-100)
  response?: any;           // Server response
  error?: any;              // Error information
  originFileObj?: File;     // Original File object
  thumbUrl?: string;        // Thumbnail URL
  filename?: string;        // Filename (alternative to name)
  lastModified?: string;    // Last modified date string
  lastModifiedDate?: Date;  // Last modified Date object
  linkProps?: { download: string }; // Link properties for download
}
```

## TDSUploadChangeParam structure

```typescript
interface TDSUploadChangeParam {
  file: TDSUploadFile;
  fileList: TDSUploadFile[];
  event?: { percent: number };
  type?: string;  // 'start' | 'progress' | 'success' | 'error' | 'removed'
}
```

## Usage

```html
<!-- Basic upload -->
<tds-upload
  [action]="'/api/upload'"
  [(fileList)]="fileList">
  <button tds-button>Click to Upload</button>
</tds-upload>

<!-- Drag & drop -->
<tds-upload
  type="drag"
  [action]="'/api/upload'"
  [(fileList)]="fileList">
  <p class="ant-upload-drag-icon">
    <i class="tdsi-cloud-upload"></i>
  </p>
  <p>Click or drag file to this area to upload</p>
</tds-upload>

<!-- Picture card list -->
<tds-upload
  listType="picture-card"
  [action]="'/api/upload'"
  [(fileList)]="fileList">
  <i class="tdsi-plus"></i>
</tds-upload>

<!-- With restrictions -->
<tds-upload
  [action]="'/api/upload'"
  [accept]="'.jpg,.png,.pdf'"
  [limit]="5"
  [size]="2048"
  [multiple]="true"
  [(fileList)]="fileList">
  <button tds-button>Upload Files</button>
</tds-upload>

<!-- Custom request -->
<tds-upload
  [customRequest]="customUpload"
  [(fileList)]="fileList">
  <button tds-button>Upload</button>
</tds-upload>
```

```typescript
import { TDSUploadModule } from 'tds-ui/upload';

@Component({
  standalone: true,
  imports: [TDSUploadModule, TDSButtonModule],
})
export class MyComponent {
  fileList: TDSUploadFile[] = [];

  // Custom upload với axios
  customUpload = (item: TDSUploadXHRArgs) => {
    const formData = new FormData();
    formData.append('file', item.file as any);
    formData.append('userId', '123');

    return axios.post('/api/upload', formData, {
      onUploadProgress: (e) => {
        item.onProgress({ percent: (e.loaded / e.total) * 100 }, item.file);
      }
    }).subscribe({
      next: (res) => item.onSuccess(res.data, item.file, item.xhr),
      error: (err) => item.onError(err, item.file)
    });
  };

  // Filter files
  beforeUpload = (file: TDSUploadFile, fileList: TDSUploadFile[]) => {
    const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
    if (!isJpgOrPng) {
      console.error('Chỉ chấp nhận JPG/PNG!');
      return false;
    }
    const isLt2M = file.size! / 1024 / 1024 < 2;
    if (!isLt2M) {
      console.error('File phải nhỏ hơn 2MB!');
      return false;
    }
    return true;
  };
}
```

## Notes

- Dùng `[(fileList)]` để two-way binding danh sách file
- `type="drag"` cho giao diện kéo thả
- `listType="picture-card"` cho giao diện gallery ảnh
- `limit` và `size` dùng để giới hạn số lượng và kích thước
- `customRequest` khi cần custom upload logic (token, auth, etc.)
- `beforeUpload` return `false` để hủy upload, return `Observable<boolean>` cho async validation
- `filter` input cho phép custom filter logic phức tạp
- Component tự động quản lý progress và trạng thái upload
- Hỗ trợ RTL (right-to-left) layout
